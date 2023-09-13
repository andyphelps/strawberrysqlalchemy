import dataclasses
from types import NoneType
from typing import List, Optional, get_origin, cast, Type, TypeVar, get_args, Union

import strawberry.object_type
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship, registry

from strawchemy.directives.lookup import Lookup
from strawchemy.mapped_types import MAPPED_TYPES
from strawchemy.utils import snake_it

reg = registry()
T = TypeVar("T")


def create_sqlalchemy_types(model_dataclasses: List[type]) -> None:
    for type_ in model_dataclasses:
        type_.__tablename__ = snake_it(type_.__name__)

        for field in dataclasses.fields(type_):
            is_optional: bool = False

            if (get_origin(field.type) == Union
                    and len(get_args(field.type)) == 2
                    and get_args(field.type)[-1] == NoneType):
                field.type = get_args(field.type)[0]
                is_optional = True

            if field.name == "id":
                setattr(type_, "id", mapped_column(primary_key=(field.name == "id")))
                type_.__annotations__["id"] = Mapped[int]
            elif field.type in model_dataclasses:
                # Add a field_id column to this model with a FK to the id of the referenced model
                # cascade only if target type isn't a lookup type

                cascade = (None
                           if Lookup() in strawberry.object_type.get_object_definition(field.type).directives
                           else "CASCADE"
                           )
                field_type_name = snake_it(field.type.__name__)
                setattr(type_,
                        f"{field_type_name}_id",
                        mapped_column(ForeignKey(f"{field_type_name}.id",
                                                 ondelete=cascade))
                        )
                type_.__annotations__[f"{field_type_name}_id"] = Mapped[Optional[int] if is_optional else int]

                setattr(type_,
                        field.name,
                        relationship(field.type, foreign_keys=[getattr(type_, f"{field_type_name}_id")])
                        )
                type_.__annotations__[field.name] = Mapped[Optional[field.type] if is_optional else field.type]

            elif get_origin(field.type) == list:
                # Add a FK'd column to the child model to support the 1 to many
                child_type = get_args(field.type)[0]
                cascade = (None
                           if Lookup() in strawberry.object_type.get_object_definition(child_type).directives
                           else "all, delete")
                setattr(child_type,
                        f"{type_.__tablename__}_id",
                        mapped_column(ForeignKey(f"{type_.__tablename__}.id",
                                                 ondelete="CASCADE" if cascade else None))
                        )
                child_type.__annotations__[f"{type_.__tablename__}_id"] = Mapped[int]

                # Add a relationship member to parent model to hold the list
                setattr(type_,
                        field.name,
                        relationship(child_type, cascade=cascade, foreign_keys=getattr(child_type,
                        f"{type_.__tablename__}_id"))
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

    for type_ in model_dataclasses:
        reg.mapped(cast(Type[T], type_))
