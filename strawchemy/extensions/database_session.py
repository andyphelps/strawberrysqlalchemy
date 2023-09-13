from sqlalchemy import Engine
from sqlalchemy.orm import Session
from strawberry.extensions import SchemaExtension
from strawberry.types import ExecutionContext
from strawberry.utils.await_maybe import AsyncIteratorOrIterator

import logging


class DatabaseSessionExtension(SchemaExtension):
    __engine: Engine

    def __init__(self, *, execution_context: ExecutionContext = None):
        super().__init__(execution_context=execution_context)

        if (not hasattr(execution_context.schema, "strawchemy_engine")
                or not getattr(execution_context.schema, "strawchemy_engine")):
            raise AttributeError("Cannot use this extension without schema having a strawchemy_engine property")

        self.__engine = getattr(execution_context.schema, "strawchemy_engine")

    def on_operation(self) -> AsyncIteratorOrIterator[None]:
        with Session(self.__engine, autoflush=False) as session:
            logging.info("Starting session")
            self.execution_context.context["session"] = session

            yield

            logging.info("Closing session")
            session.close()
