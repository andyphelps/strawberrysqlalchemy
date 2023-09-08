import dataclasses
from typing import get_origin, get_args, Optional, List

from strawberrysqlalchemy.strawchemy.mapped_types import MAPPED_TYPES


def validate_model_classes(model_classes: List[type]) -> None:
    for type_ in model_classes:
        if ("id", int) not in [(field.name, field.type) for field in dataclasses.fields(type_)]:
            raise ValueError(f"Dataclass {type_.__name__} does not define an 'id' member of type 'int'")

        for field in dataclasses.fields(type_):
            if get_origin(field.type) == list:
                if get_args(field.type)[0] not in model_classes:
                    raise ValueError(
                        f"Dataclass {type_.__name__} has list field with a disallowed type: {field.name}: {field.type}"
                    )
            elif field.type not in set(MAPPED_TYPES.keys()).union(set(model_classes)):
                raise ValueError(
                    f"Dataclass {type_.__name__} has field with a disallowed type: {field.name}: {field.type}"
                )


def ensure_nullable_ids(model_dataclasses: List[type]) -> None:
    for type_ in model_dataclasses:
        id_field: dataclasses.field = next(field for field in dataclasses.fields(type_) if field.name == "id")

        if id_field.type != Optional[int]:
            id_field.type = Optional[int]
            id_field.default = None
