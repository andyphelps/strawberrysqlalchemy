from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session
from strawberry.extensions import SchemaExtension
from strawberry.types import ExecutionContext
from strawberry.utils.await_maybe import AsyncIteratorOrIterator

from strawberrysqlalchemy.model.entity import reg


class DatabaseSessionExtension(SchemaExtension):
    engine: Engine

    def __init__(self, *, execution_context: ExecutionContext):
        super().__init__(execution_context=execution_context)
        self.engine = create_engine("sqlite:///sqlite.db", echo=True)
        reg.metadata.create_all(self.engine)

    def on_operation(self) -> AsyncIteratorOrIterator[None]:
        with Session(self.engine) as session:
            self.execution_context.context["session"] = session
            yield
            self.execution_context.context["session"].close()
