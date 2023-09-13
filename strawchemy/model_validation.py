from typing import List

import strawberry.object_type
from strawberry.type import StrawberryList, StrawberryOptional

from strawchemy.mapped_types import MAPPED_TYPES


def validate_model_classes(model_classes: List[type]) -> None:
    allowed_types = set(MAPPED_TYPES.keys()).union(set(model_classes))

    for type_ in model_classes:
        if ("id", int) not in [(field.name, field.type)
                               for field in strawberry.object_type.get_object_definition(type_).fields]:
            raise AttributeError(f"Type {type_.__name__} does not define an 'id' member of type 'int'")

        for field in strawberry.object_type.get_object_definition(type_).fields:
            if (type(field.type) in (StrawberryOptional, StrawberryList)
                    and type(field.type.of_type) in (StrawberryOptional, StrawberryList)):
                raise AttributeError(
                    f"Type {type_.__name__} has a list of optional or a optional of list type on "
                    f"field '{field.name}' with type '{field.type.of_type.of_type.__name__}' "
                    f"and nesting these types isn't allowed"
                )
            elif type(field.type) == StrawberryList:
                if field.type.of_type not in model_classes:
                    raise AttributeError(
                        f"Type {type_.__name__} has a list field with a disallowed "
                        f"type '{field.type.of_type.__name__}' on field '{field.name}'"
                    )
            elif type(field.type) == StrawberryOptional:
                if field.type.of_type not in allowed_types:
                    raise AttributeError(
                        f"Type {type_.__name__} has an optional field with a disallowed "
                        f"type '{field.type.of_type.__name__}' on field '{field.name}'"
                    )
            elif field.type not in allowed_types:
                raise AttributeError(
                    f"Type {type_.__name__} has field with a disallowed "
                    f"type '{field.type.__name__}' on field '{field.name}'"
                )
