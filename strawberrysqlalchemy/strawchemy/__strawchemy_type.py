import dataclasses
import inspect
from typing import Type, Any, Callable

import typing

import strawberry
from strawberry.types.types import StrawberryObjectDefinition


def __is_strawberry_type(cls: Type[Any]) -> bool:
    return isinstance(getattr(cls, "__strawberry_definition__", None), StrawberryObjectDefinition)


def type(config: int | Type[Any]) -> Callable:
    def strawberry_sqlalchemy_type(cls: Type[Any]) -> Type[Any]:
        if not inspect.isclass(cls):
            raise TypeError("Can only use @strawberry_sqlalchemy decorator on classes")

        cls.id = strawberry.field(default=None, graphql_type=typing.Optional[int])

        cls = strawberry.type(cls)

        for field in getattr(cls, "__strawberry_definition__").fields:
            origin = typing.get_origin(field.type)

            if origin == list:
                fk_type: Type[Any] = typing.get_args(field.type)[0]

                if not getattr(fk_type, "__has_strawberry_sqlalchemy_magic__", False):
                    raise TypeError(
                        "Cannot use lists of types that are not part of the model")

                # Add FK

            if __is_strawberry_type(field.type):
                # Add FK
                pass
        cls.__has_strawberry_sqlalchemy_magic__ = True

        return cls

    if inspect.isclass(config):
        return strawberry_sqlalchemy_type(config)
    else:
        return strawberry_sqlalchemy_type
