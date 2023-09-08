from typing import Iterable, List, Type, TypeVar

import strawberry
from sqlalchemy import select
from sqlalchemy.orm import Session
from strawberry.field import StrawberryField
from strawberry.type import StrawberryList, StrawberryOptional
from toolz import curry

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")


def create_strawberry_types(model_dataclasses: List[Type]) -> None:
    for type_ in model_dataclasses:
        strawberry.type(type_)
        id_field = next(field
                        for field in strawberry.object_type.get_object_definition(type_).fields
                        if field.python_name == "id")
        id_field.type = strawberry.Private[id_field.type]


def __lookup_items_with_ids(obj: T, session: Session) -> None:
    for field in strawberry.object_type.get_object_definition(obj).fields:
        field_value = getattr(obj, field.python_name)

        if strawberry.object_type.get_object_definition(field.type) and field_value:
            if not getattr(field_value, "id") is None:
                statement = select(field.type).where(field.type.id == field_value.id)
                loaded_value = session.execute(statement).unique().scalars().one_or_none()
                if loaded_value:
                    setattr(obj, field.python_name, loaded_value)
            else:
                __lookup_items_with_ids(field_value, session)


@curry
def make_object(type_: T, input_: U, session: Session) -> T:
    obj_dict = {}

    for field in strawberry.object_type.get_object_definition(input_).fields:
        input_value = getattr(input_, field.python_name)
        field_type = field.type.of_type if type(field.type) == StrawberryOptional else field.type

        if input_value is None:
            obj_dict[field.python_name] = [] if type(field_type) == StrawberryList else None
        elif strawberry.object_type.get_object_definition(field_type):
            obj_type = strawberry.object_type.get_object_definition(type_).get_field(field.python_name).type
            obj_dict[field.python_name] = make_object(obj_type, input_value, session)
        elif type(field_type) == StrawberryList:
            obj_type = strawberry.object_type.get_object_definition(type_).get_field(field.python_name).type.of_type
            obj_dict[field.python_name] = [make_object(obj_type, item, session) for item in input_value]
        else:
            obj_dict[field.python_name] = input_value

    obj = type_(**obj_dict)
    __lookup_items_with_ids(obj, session)

    return obj


def merge_lists(existing: List[T], update: List[U], session: Session) -> None:
    for item in update:
        if item.id:
            existing_item = next(x for x in existing if x.id == item.id)
            if existing_item:
                update_object(item, existing_item, session)
            else:
                raise ValueError("Item in list with id that does not exist")
        else:
            obj = make_object(type(item).__strawchemy_origin_type__, item, session)
            __lookup_items_with_ids(obj, session)
            existing.append(obj)


def update_object(input_: U, object_to_update: T, session: Session) -> T:
    if not input_.id:
        return make_object(input_.__strawchemy_origin_type__, input_, session)

    non_null_fields = [field
                       for field in strawberry.object_type.get_object_definition(input_).fields
                       if getattr(input_, field.python_name) and field.python_name != "id"]

    for field in non_null_fields:
        input_value = getattr(input_, field.python_name)
        original_value = getattr(object_to_update, field.python_name)
        field_type = field.type.of_type

        if strawberry.object_type.get_object_definition(input_value):
            setattr(object_to_update, field.python_name, update_object(input_value, original_value, session))
        elif type(field_type) == StrawberryList:
            merge_lists(original_value, input_value, session)
        else:
            setattr(object_to_update, field.python_name, input_value)

    return object_to_update


def recursively_create_strawberry_create_types(type_: Type) -> None:
    if hasattr(type_, "__strawchemy_create_type__"):
        return

    type_.__strawchemy_create_type__ = strawberry.input(type(f"{type_.__name__}Create", (), dict(type_.__dict__)))
    type_.__strawchemy_create_type__.make_object = make_object(type_)
    type_.__strawchemy_create_type__.__strawchemy_origin_type__ = type_

    fields: Iterable[StrawberryField] = [
        field
        for field in strawberry.object_type.get_object_definition(type_.__strawchemy_create_type__).fields
    ]

    for field in fields:
        if type(field.type) == StrawberryList:
            recursively_create_strawberry_create_types(field.type.of_type)
            field.type = StrawberryList(of_type=field.type.of_type.__strawchemy_create_type__)
        elif strawberry.object_type.get_object_definition(field.type):
            recursively_create_strawberry_create_types(field.type)
            field.type = field.type.__strawchemy_create_type__
        elif field.python_name == "id":
            field.type = StrawberryOptional(of_type=field.type)
            field.default_value = None


def recursively_create_strawberry_update_types(type_: Type) -> None:
    if hasattr(type_, "__strawchemy_update_type__"):
        return

    type_.__strawchemy_update_type__ = strawberry.input(type(f"{type_.__name__}Update", (), dict(type_.__dict__)))
    type_.__strawchemy_update_type__.update_object = update_object
    type_.__strawchemy_update_type__.__strawchemy_origin_type__ = type_

    fields: Iterable[StrawberryField] = [
        field
        for field in strawberry.object_type.get_object_definition(type_.__strawchemy_update_type__).fields
    ]

    for field in fields:
        if type(field.type) == StrawberryList:
            recursively_create_strawberry_update_types(field.type.of_type)
            field.type = StrawberryOptional(
                of_type=StrawberryList(
                    of_type=StrawberryOptional(
                        of_type=field.type.of_type.__strawchemy_update_type__
                    )
                )
            )
            field.default_value = None
        elif strawberry.object_type.get_object_definition(field.type):
            recursively_create_strawberry_update_types(field.type)
            field.type = StrawberryOptional(of_type=field.type.__strawchemy_update_type__)
            field.default_value = None
        elif type(field.type) != StrawberryOptional:
            field.type = StrawberryOptional(of_type=field.type)
            field.default_value = None
