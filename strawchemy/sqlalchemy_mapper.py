from typing import List, Optional, cast, Type, TypeVar

from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship, registry
from strawberry.object_type import get_object_definition  # noqa
from strawberry.type import StrawberryOptional, StrawberryList

from strawchemy.directives.lookup import Lookup
from strawchemy.mapped_types import MAPPED_TYPES
from strawchemy.utils import snake_it

reg = registry()
T = TypeVar("T")


def create_sqlalchemy_types(model_classes: List[type]) -> None:
    for type_ in model_classes:
        type_.__tablename__ = snake_it(type_.__name__)

        for field in get_object_definition(type_).fields:
            is_optional: bool = False

            if type(field.type) == StrawberryOptional:
                field.type = field.type.of_type
                is_optional = True

            if field.name == "id":
                setattr(type_, "id", mapped_column(primary_key=(field.name == "id")))
                type_.__annotations__["id"] = Mapped[int]
            elif field.type in model_classes:
                # Add a field_id column to this model with a FK to the id of the referenced model
                # cascade only if target type isn't a lookup type

                child_table_name = snake_it(field.type.__name__)
                field_name = f"{field.name}_id"

                cascade = (None
                           if Lookup() in get_object_definition(field.type).directives
                           else "CASCADE"
                           )

                setattr(type_,
                        field_name,
                        mapped_column(ForeignKey(f"{child_table_name}.id",
                                                 ondelete=cascade))
                        )

                type_.__annotations__[field_name] = Mapped[Optional[int] if is_optional else int]

                setattr(type_,
                        field.name,
                        relationship(field.type, foreign_keys=[getattr(type_, field_name)])
                        )

                type_.__annotations__[field.name] = Mapped[Optional[field.type] if is_optional else field.type]

            elif type(field.type) == StrawberryList:
                # Add a FK'd column to the child model to support the 1 to many

                child_type = field.type.of_type
                child_field_name = f"{type_.__tablename__}_id"

                cascade = (None
                           if Lookup() in get_object_definition(child_type).directives
                           else "all, delete")

                setattr(child_type,
                        child_field_name,
                        mapped_column(ForeignKey(f"{type_.__tablename__}.id",
                                                 ondelete="CASCADE" if cascade else None))
                        )

                child_type.__annotations__[child_field_name] = Mapped[int]

                # Add a relationship member to parent model to hold the list
                setattr(type_,
                        field.name,
                        relationship(child_type, cascade=cascade, foreign_keys=getattr(child_type, child_field_name))
                        )
                type_.__annotations__[field.name] = Mapped[(Optional[List[child_type]]
                                                            if is_optional
                                                            else List[child_type])]
            else:
                setattr(type_,
                        field.name,
                        mapped_column(MAPPED_TYPES[field.type], nullable=is_optional)
                        )

                type_.__annotations__[field.name] = Mapped[Optional[field.type] if is_optional else field.type]

    for type_ in model_classes:
        reg.mapped(cast(Type[T], type_))
