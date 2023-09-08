import dataclasses
from typing import List, Optional, get_origin, cast, Type, TypeVar, get_args, Set

from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship, registry

from strawberrysqlalchemy.strawchemy.mapped_types import MAPPED_TYPES
from strawberrysqlalchemy.strawchemy.utils import snake_it

reg = registry()
T = TypeVar("T")


def create_sqlalchemy_types(model_dataclasses: List[type]) -> None:
    for type_ in model_dataclasses:
        type_.__tablename__ = snake_it(type_.__name__)

        for field in dataclasses.fields(type_):
            if field.name == "id":
                setattr(type_, "id", mapped_column(primary_key=(field.name == "id")))
                type_.__annotations__["id"] = Mapped[int]
            elif field.type in model_dataclasses:
                # Add a field_id column to this model with a FK to the id of the referenced model
                field_type_name = snake_it(field.type.__name__)
                setattr(type_,
                        f"{field_type_name}_id",
                        mapped_column(ForeignKey(f"{field_type_name}.id"))
                        )
                type_.__annotations__[f"{field_type_name}_id"] = Mapped[Optional[int]]

                setattr(type_,
                        field.name,
                        relationship(field.type, lazy="joined")
                        )
                type_.__annotations__[field.name] = Mapped[field.type]

            elif get_origin(field.type) == list:
                # Add a FK'd column to the referenced model to support the 1 to many
                # target_type = self.__model_dataclasses[get_args(field.type)[0].__name__].__sqlalchemy_type__
                target_type = get_args(field.type)[0]
                setattr(target_type,
                        f"{type_.__tablename__}_id",
                        mapped_column(ForeignKey(f"{type_.__tablename__}.id"))
                        )
                target_type.__annotations__[f"{type_.__tablename__}_id"] = Mapped[Optional[int]]

                # Add a relationship member to this model to hold the list
                setattr(type_,
                        field.name,
                        relationship(target_type, lazy="joined")
                        )
                type_.__annotations__[field.name] = Mapped[List[target_type]]
            else:
                setattr(type_,
                        field.name,
                        mapped_column(MAPPED_TYPES[field.type])
                        )
                type_.__annotations__[field.name] = Mapped[field.type]

    for type_ in model_dataclasses:
        # type_.__sqlalchemy_type__ = reg.mapped(cast(Type[T], type_.__sqlalchemy_type__))
        reg.mapped(cast(Type[T], type_))

