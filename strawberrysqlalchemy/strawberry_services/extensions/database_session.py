from sqlalchemy import Engine
from sqlalchemy.orm import Session
from strawberry.extensions import SchemaExtension
from strawberry.types import ExecutionContext
from strawberry.utils.await_maybe import AsyncIteratorOrIterator


class DatabaseSessionExtension(SchemaExtension):
    __engine: Engine

    def __init__(self, *, execution_context: ExecutionContext = None):
        super().__init__(execution_context=execution_context)

        if not hasattr(execution_context.schema, "__engine__"):
            raise AttributeError("Cannot use this extension without an __engine__ defined")

        self.__engine = execution_context.schema.__engine__

    def on_operation(self) -> AsyncIteratorOrIterator[None]:
        with Session(self.__engine, autoflush=False) as session:
            self.execution_context.context["session"] = session
            yield
            self.execution_context.context["session"].close()
