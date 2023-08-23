from datetime import datetime, date, time, timedelta
from typing import Callable, TypeVar, Type, Optional, List, Dict

import strawberry
from sqlalchemy import Integer, String, Float, DateTime, LargeBinary, Boolean, Date, Time, Interval, ARRAY, JSON, \
    column, ColumnClause
from sqlalchemy.orm import registry, Relationship, relationship
from strawberry.types.types import StrawberryObjectDefinition
from strawberry.utils.typing import is_list

T = TypeVar("T", bound=Type)

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
orm_reg = registry()


def type(cls: Optional[T], *, name: Optional[str] = None) -> Callable[[T], T]:  # noqa
    def wrap(wrapped_cls: Type) -> Type:
        strawberry_cls: Type = strawberry.type(wrapped_cls)

        sod: StrawberryObjectDefinition = strawberry.object_type.get_object_definition(strawberry_cls)

        if not sod.get_field("id"):
            raise TypeError("Strawchemy types must define an 'id' field as a primary key")

        relationships: Dict[str, Relationship] = {
            field.python_name: relationship(field.type, cascade="all, delete-orphan")
            for field in sod.fields
            if is_list(field.type_annotation.annotation)
        }

        columns: List[ColumnClause] = [
            column(field.name, TYPE_MAP.get(field.type))
            for field in sod.fields
            if not (is_list(field.type_annotation.annotation))
        ]
        strawberry_cls.__mapper_args__ = {
            "properties": relationships
        }

        return orm_reg.mapped(strawberry_cls)

    if cls:
        return wrap(cls)
    else:
        raise TypeError("Can only use strawchemy.type as a decorator on classes")
