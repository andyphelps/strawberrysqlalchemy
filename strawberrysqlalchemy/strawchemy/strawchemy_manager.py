import dataclasses
import inspect
import pkgutil
import re
from datetime import datetime, date, time
from itertools import chain
from types import ModuleType
from typing import TypeVar, List, Callable, Optional, Iterable, Dict, get_origin, get_args, Type, cast

import sqlalchemy
import strawberry
import strawberry.types
from sqlalchemy import create_engine, Integer, Float, String, Boolean, Date, Time, DateTime, text, ForeignKey
from sqlalchemy.orm import registry, DeclarativeBase, Session, mapped_column, Mapped, relationship
from strawberry.field import StrawberryField
from strawberry.type import StrawberryList, StrawberryOptional

T = TypeVar("T")
U = TypeVar("U")
MAPPED_TYPES: Dict[type, type] = {
    int: Integer,
    float: Float,
    str: String,
    bool: Boolean,
    datetime: DateTime,
    date: Date,
    time: Time,

}

reg = registry()


class Base(DeclarativeBase):
    metadata = reg.metadata


class StrawchemyManager:
    __engine: sqlalchemy.Engine
    __model_dataclasses: Dict[str, type]

    def __init__(self, engine: str, model_package_name: str) -> None:
        self.__engine = create_engine(engine, echo=True)
        self.__discover_model_dataclasses(model_package_name)
        self.__validate_model_dataclasses()
        self.__create_strawberry_types(strawberry.type, "__strawberry_type__", "")
        self.__create_strawberry_types(strawberry.input, "__strawberry_input_type__", "Input", True)
        self.__create_sqlalchemy_types()

        reg.metadata.create_all(self.__engine)

        with Session(self.__engine) as s:
            df1 = self.__model_dataclasses["Datafile"].__sqlalchemy_type__(name="DF1")
            ds1 = self.__model_dataclasses["Dataset"].__sqlalchemy_type__(name="DS1", datafiles=[df1])
            ...

        ...

    def __run_sql(self, sql: str) -> List[str]:
        with self.__engine.connect() as c:
            return list(c.execute(text(sql)))

    def __discover_model_dataclasses(self, model_package_name) -> None:
        model_package: ModuleType = pkgutil.resolve_name(model_package_name)

        model_modules: Iterable[ModuleType] = (
            pkgutil.resolve_name(module_info.name) for module_info in
            pkgutil.walk_packages(model_package.__path__, prefix=f"{model_package.__name__}.")
            if not module_info.ispkg
        )

        self.__model_dataclasses = {x[0]: x[1] for x in chain.from_iterable(
            inspect.getmembers(module, dataclasses.is_dataclass)
            for module in model_modules
        )}

    def __validate_model_dataclasses(self) -> None:
        for type_ in self.__model_dataclasses.values():
            if ("id", int) not in [(field.name, field.type) for field in dataclasses.fields(type_)]:
                raise ValueError(f"Dataclass {type_.__name__} does not define an 'id' member of type 'int'")

            for field in dataclasses.fields(type_):
                if get_origin(field.type) == list:
                    if get_args(field.type)[0] not in self.__model_dataclasses.values():
                        raise ValueError(
                            f"Dataclass {type_.__name__} has list field with a disallowed type: {field.name}: {field.type}"
                        )
                elif field.type not in set(MAPPED_TYPES.keys()).union(set(self.__model_dataclasses.values())):
                    raise ValueError(
                        f"Dataclass {type_.__name__} has field with a disallowed type: {field.name}: {field.type}"
                    )

    def __create_strawberry_types(self, conversion_fn: Callable, member_name: str, suffix: str,
                                  optional_fields: bool = False) -> None:
        for name, type_ in self.__model_dataclasses.items():
            strawberry_type = conversion_fn(type(name + suffix, (), dict(type_.__dict__)))
            setattr(type_, member_name, strawberry_type)

        fields: Iterable[StrawberryField] = (
            field
            for type_ in self.__model_dataclasses.values()
            for field in strawberry.object_type.get_object_definition(getattr(type_, member_name)).fields
        )

        for field in fields:
            if type(field.type) == StrawberryList:
                field.type = StrawberryList(of_type=getattr(field.type.of_type, member_name))
            elif field.type in self.__model_dataclasses.values():
                field.type = getattr(field.type, member_name)

            if optional_fields:
                field.type = StrawberryOptional(of_type=field.type)
                field.default_value = None

    def __create_sqlalchemy_types(self) -> None:
        for name, type_ in self.__model_dataclasses.items():
            sqlalchemy_type = type(f"{name}Db", (), {})
            sqlalchemy_type.__tablename__ = self.__snake_it(name)
            type_.__sqlalchemy_type__ = sqlalchemy_type

        for name, type_ in self.__model_dataclasses.items():
            sqlalchemy_type = type_.__sqlalchemy_type__

            for field in dataclasses.fields(type_):
                if field.name == "id":
                    setattr(sqlalchemy_type, "id", mapped_column(primary_key=(field.name == "id")))
                    sqlalchemy_type.__annotations__["id"] = Mapped[int]
                elif field.type in self.__model_dataclasses.values():
                    # Add a field_id column to this model with a FK to the id of the referenced model
                    field_type_name = self.__snake_it(field.type.__name__)
                    setattr(sqlalchemy_type,
                            f"{field_type_name}_id",
                            mapped_column(ForeignKey(f"{field_type_name}.id"))
                            )
                    sqlalchemy_type.__annotations__[f"{field_type_name}_id"] = Mapped[Optional[int]]

                    setattr(sqlalchemy_type,
                            field.name,
                            relationship(field.type.__sqlalchemy_type__)
                            )
                    sqlalchemy_type.__annotations__[field.name] = Mapped[field.type.__sqlalchemy_type__]

                elif get_origin(field.type) == list:
                    # Add a FK'd column to the referenced model to support the 1 to many
                    target_type = self.__model_dataclasses[get_args(field.type)[0].__name__].__sqlalchemy_type__
                    setattr(target_type,
                            f"{sqlalchemy_type.__tablename__}_id",
                            mapped_column(ForeignKey(f"{sqlalchemy_type.__tablename__}.id"))
                            )
                    target_type.__annotations__[f"{sqlalchemy_type.__tablename__}_id"] = Mapped[Optional[int]]

                    # Add a relationship member to this model to hold the list
                    setattr(sqlalchemy_type,
                            field.name,
                            relationship(target_type)
                            )
                    sqlalchemy_type.__annotations__[field.name] = Mapped[List[target_type]]
                else:
                    setattr(sqlalchemy_type,
                            field.name,
                            mapped_column(MAPPED_TYPES[field.type])
                            )
                    sqlalchemy_type.__annotations__[field.name] = Mapped[field.type]

        for name, type_ in self.__model_dataclasses.items():
            type_.__sqlalchemy_type__ = reg.mapped(cast(Type[T], type_.__sqlalchemy_type__))

    @staticmethod
    def __snake_it(value: str) -> str:
        return re.sub(r"(?<!^)(?=[A-Z])", "_", value).lower()

    @staticmethod
    def __add_attr(type_: T, cls: U, suffix: str, resolver: Callable) -> None:
        name = f"{cls.__name__}{suffix}"
        setattr(type_, name, strawberry.field(resolver=resolver))
        type_.__annotations__[name] = inspect.get_annotations(resolver)["return"]

    @property
    def schema(self) -> strawberry.schema.BaseSchema:
        query_type = type("Query", (), {})
        mutation_type = type("Mutation", (), {})

        for model_class in self.__model_dataclasses.values():
            def get_data(info: strawberry.types.Info) -> List[model_class.__strawberry_type__]:
                return []

            def get_data_by_id(_id: int, info: strawberry.types.Info) -> Optional[model_class.__strawberry_type__]:
                return None

            def upsert(input: model_class.__strawberry_input_type__, info: strawberry.types.Info) -> Optional[
                model_class.__strawberry_type__]:
                return None

            def delete(id: int, info: strawberry.types.Info) -> bool:
                return True

            self.__add_attr(query_type, model_class.__strawberry_type__, "All", get_data)
            self.__add_attr(query_type, model_class.__strawberry_type__, "ById", get_data_by_id)
            self.__add_attr(mutation_type, model_class.__strawberry_type__, "Upsert", upsert)
            self.__add_attr(mutation_type, model_class.__strawberry_type__, "Delete", delete)

        return strawberry.Schema(query=strawberry.type(query_type), mutation=strawberry.type(mutation_type))
