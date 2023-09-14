from typing import TypeVar, Optional, Type, get_origin, List

import sqlalchemy
import strawberry
from sqlalchemy import create_engine, Engine, Select, select, Result
from sqlalchemy.orm import Session
from strawberry.type import get_object_definition
from strawberry.types import Info
from strawberry.types.fields.resolver import StrawberryResolver
from strawberry.types.types import StrawberryObjectDefinition

from strawchemy.extensions import ErrorHandlerExtension, DatabaseSessionExtension
from strawchemy.model_validation import validate_model_classes
from strawchemy.sqlalchemy_mapper import create_sqlalchemy_types, reg
from strawchemy.strawberry_conversion import recursively_create_strawberry_create_types, \
    recursively_create_strawberry_update_types

T = TypeVar("T")
U = TypeVar("U")


class StrawchemyManager:
    __engine: sqlalchemy.Engine
    __query: Type
    __mutation: Optional[Type]

    def __init__(self, engine: str,
                 query: Type,
                 mutation: Optional[Type] = None,
                 ) -> None:
        self.__engine = create_engine(engine, echo=True)
        self.__query = query
        self.__mutation = mutation

    @property
    def engine(self) -> Engine:
        return self.__engine

    @property
    def schema(self) -> strawberry.schema.BaseSchema:
        for field in get_object_definition(self.__query).fields:

            if "fetchall" in field.python_name.lower():
                def resolve_all(info: Info) -> field.type:
                    statement: Select = select(info.return_type.of_type)
                    session: Session = info.context["session"]

                    return session.execute(statement).scalars().unique().fetchall()

                field.base_resolver = StrawberryResolver(resolve_all)
            elif "fetch" in field.python_name.lower() and "byid" in field.python_name.lower():
                if get_origin(field.type) == list:
                    raise ValueError("Fetch..ById Query members cannot be lists")

                def resolve_by_id(id: int, info: Info) -> field.type:
                    statement: Select = select(info.return_type.of_type).where(info.return_type.of_type.id == id)
                    session: Session = info.context["session"]
                    result: Result = session.execute(statement)
                    return result.scalars().unique().one_or_none()

                field.base_resolver = StrawberryResolver(resolve_by_id)
            else:
                raise ValueError("Query members must have FetchAll or FetchById in their names (type insensitive)")

        for field in get_object_definition(self.__mutation).fields if self.__mutation else []:
            recursively_create_strawberry_create_types(field.type)
            recursively_create_strawberry_update_types(field.type)

            if field.python_name.lower().startswith("create"):

                def mutate_create(input_: field.type.__strawchemy_create_type__, info: Info) -> field.type:
                    session: Session = info.context["session"]
                    obj = input_.make_object(session)
                    session.add(obj)
                    session.commit()

                    return obj

                field.base_resolver = StrawberryResolver(mutate_create)

            if field.python_name.lower().startswith("update"):

                def mutate_update(input_: field.type.__strawchemy_update_type__, info: Info) -> field.type:
                    session: Session = info.context["session"]

                    if not input_.id:
                        raise ValueError("Missing 'id' on update mutation input parameter")

                    obj = session.get(info.return_type, input_.id)

                    if not obj:
                        raise LookupError(f"Could not find {info.return_type.__name__} with id: '{input_.id}'")

                    obj = input_.update_object(obj, session)
                    session.commit()

                    return obj

                field.base_resolver = StrawberryResolver(mutate_update)

            if field.python_name.lower().startswith("delete"):
                def mutate_delete(id_: int, info: Info) -> field.type:
                    session: Session = info.context["session"]
                    obj = session.get(field.type, id_)

                    if not obj:
                        raise LookupError(f"Could not find {info.return_type.__name__} with id: '{id_}'")

                    session.delete(obj)
                    session.commit()

                    return obj

                field.base_resolver = StrawberryResolver(mutate_delete)

        schema: strawberry.Schema = strawberry.Schema(query=self.__query,
                                                      mutation=self.__mutation,
                                                      extensions=[ErrorHandlerExtension, DatabaseSessionExtension])
        schema.strawchemy_engine = self.__engine

        schema_types: List[Type] = [schema_type.definition.origin
                                    for schema_type in schema.schema_converter.type_map.values()
                                    if type(schema_type.definition) == StrawberryObjectDefinition
                                    and schema_type.definition.origin not in (schema.query, schema.mutation)
                                    and not schema_type.definition.is_input]

        validate_model_classes(schema_types)
        create_sqlalchemy_types(schema_types)

        # reg.metadata.drop_all(self.engine)
        reg.metadata.create_all(self.engine, checkfirst=False)

        return schema
