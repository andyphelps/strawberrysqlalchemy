import dataclasses
import inspect
import re
import typing
from datetime import datetime, date, time, timedelta
from itertools import chain
from typing import TypeVar, List, Dict, Optional, Set

import strawberry
from sqlalchemy import Engine, Table, Column, Integer, String, Float, DateTime, LargeBinary, Boolean, Date, \
    Time, Interval, ARRAY, JSON, ForeignKey
from sqlalchemy.orm import registry
from strawberry.types import Info

from strawberrysqlalchemy.strawberry_services.extensions.database_session import DatabaseSessionExtension

T = TypeVar("T", bound=type)
U = TypeVar("U", bound=object)
V = TypeVar("V", bound=object)

reg = registry()
camel_to_snake_re = re.compile(r"(?<!^)(?=[A-Z])")
TYPE_MAP = {
    int: Integer,
    str: String,
    float: Float,
    datetime: DateTime,
    bytes: LargeBinary,
    bool: Boolean,
    date: Date,
    time: Time,
    timedelta: Interval,
    list: ARRAY,
    dict: JSON
}


class StrawchemySchema(strawberry.schema.Schema):

    def __init__(self, *, queriable_types: Set[T], mutable_types: Optional[Set[T]] = None, engine: Engine):

        mutable_types = mutable_types or {}

        if not mutable_types.issubset(queriable_types):
            raise ValueError("mutable set must be a subset of the queriable set")

        model_types: Set[T] = self.__get_nested_model_types(queriable_types)

        if not model_types:
            raise TypeError("StrawchemySchema requires at least one class type in the queriable argument")

        self.__wire_sqlalchemy_into_queriables(model_types)

        query_class = self.__make_query_object(queriable_types)
        mutation_class = self.__make_mutation_object(mutable_types)

        self.engine = engine
        reg.metadata.create_all(engine)

        super().__init__(query=strawberry.type(query_class),
                         mutation=strawberry.type(mutation_class),
                         extensions=[DatabaseSessionExtension]
                         )

    def __make_mutation_object(self, mutable):
        mutation_class = type("Mutation", (object,), {})
        for _type in mutable:
            input_type = self.__make_input_type_from_type(_type)

            def mutate(_input: input_type, info: Optional[Info] = None) -> _type:
                return self.__mutate(_input, info)

            setattr(mutation_class,
                    f"Create{_type.__name__}",
                    strawberry.mutation(resolver=mutate, name=f"Create{_type.__name__}")
                    )
            mutation_class.__annotations__[f"Create{_type.__name__}"] = _type
        return mutation_class

    def __make_query_object(self, queriable):
        query_class = type("Query", (object,), {})
        for _type in queriable:
            setattr(query_class, f"GetAll{_type.__name__}", strawberry.field(resolver=self.__query_resolver_all(_type)))
            query_class.__annotations__[f"GetAll{_type.__name__}"] = List[_type]

            setattr(query_class, f"GetById{_type.__name__}",
                    strawberry.field(resolver=self.__query_resolver_by_id(_type)))
            query_class.__annotations__[f"GetById{_type.__name__}"] = _type
        return query_class

    def __wire_sqlalchemy_into_queriables(self, model_types):
        # First pass - wire in all foreign keys of a 1..1 nature and
        # store the type and target of 1..* for the second pass

        for _type in model_types:
            columns: List[Column] = [
                Column(name, TYPE_MAP[_mtype], primary_key=(name == "id"))
                for (name, _mtype) in typing.get_type_hints(_type).items()
                if _mtype in TYPE_MAP.keys()
            ]

            foreign_keys: List[Column] = [
                Column(name, ForeignKey(f"{self.__snakeit(_mtype.__name__)}.id"))
                for (name, _mtype) in typing.get_type_hints(_type).items()
                if _mtype in model_types
            ]

            columns.extend(foreign_keys)

            _type.__one_to_many_foreign_keys__ = {
                name: resolved
                for (name, _mtype) in typing.get_type_hints(_type).items()
                if not inspect.isbuiltin(resolved := self.__get_origin_model_type(_mtype))
                   and typing.get_origin(_mtype) == list
            }

            _type.__table__ = Table(
                self.__snakeit(_type.__name__),
                reg.metadata,
                *columns
            )

        # Second pass attaches <name>_id column to child types and sets up foreign key column
        for _type in model_types:
            pass

        for _type in model_types:
            reg.mapped(strawberry.type(_type))  # noqa

    @staticmethod
    def __make_input_type_from_type(_type: typing.Type) -> typing.Type:
        input_type = type(f"{_type.__name__}Input", (object,), {})

        for (name, _mtype) in typing.get_type_hints(_type).items():
            if name != "id":
                setattr(input_type, name, _mtype())
                input_type.__annotations__[name] = _mtype

        return strawberry.input(input_type)

    @staticmethod
    def __query_resolver_all(_type: U) -> typing.Callable[[], List[U]]:
        def resolve_all(info: Optional[Info] = None) -> List[U]:
            return []

        return resolve_all

    @staticmethod
    def __query_resolver_by_id(_type: U) -> typing.Callable[[int], U]:
        def resolve_by_id(_id: int, info: Optional[Info] = None) -> U:
            return None

        return resolve_by_id

    @staticmethod
    def __mutate(_input: U, info: Info) -> V:
        return None

    @staticmethod
    def __snakeit(name: str) -> str:
        return camel_to_snake_re.sub("_", name).lower()

    def __get_nested_model_types(self, model_types: Set[T], all_model_types: Optional[Set[T]] = None) -> Set[T]:
        if not all_model_types:
            all_model_types = set()

        resolved_model_types: Set[T] = {
            resolved
            for model_type in model_types
            if (resolved := self.__get_origin_model_type(model_type)) not in typing.cast(dict, __builtins__).values()
               and inspect.isclass(resolved)
        }

        for model_type in resolved_model_types:
            all_model_types.add(model_type)
            sub_types = {
                _type
                for name, _type in typing.get_type_hints(model_type).items()
                if not name.startswith("_") and _type not in all_model_types
            }

            self.__get_nested_model_types(sub_types, all_model_types)

        return all_model_types

    @staticmethod
    def __get_origin_model_type(model_type):
        return typing.get_args(model_type)[0] if typing.get_origin(model_type) == list else model_type
