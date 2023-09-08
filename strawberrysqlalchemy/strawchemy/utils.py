import inspect
import re
from typing import Callable, TypeVar

import strawberry

T = TypeVar("T")
U = TypeVar("U")


def snake_it(value: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", value).lower()


def add_attr(type_: T, cls: U, suffix: str, resolver: Callable) -> None:
    name = f"{cls.__name__}{suffix}"
    setattr(type_, name, strawberry.field(resolver=resolver))
    type_.__annotations__[name] = inspect.get_annotations(resolver)["return"]
