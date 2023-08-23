from typing import cast

from sqlalchemy import Engine
from sqlalchemy.orm import Session, registry
from strawberry.extensions import SchemaExtension
from strawberry.types import ExecutionContext
from strawberry.utils.await_maybe import AsyncIteratorOrIterator

reg = registry()


class DatabaseSessionExtension(SchemaExtension):
    engine: Engine

    def __init__(self, *, execution_context: ExecutionContext):
        super().__init__(execution_context=execution_context)
        # if not hasattr(self, "engine"):
        #     raise ConnectionError("Cannot use DatabaseSessionExtension outside of StrawchemySchema")

        self.engine = cast("strawberrysqlalchemy.strawchemy.StrawchemySchema", execution_context.schema).engine
        reg.metadata.create_all(self.engine)

    def on_operation(self) -> AsyncIteratorOrIterator[None]:
        with Session(self.engine) as session:
            self.execution_context.context["session"] = session
            yield
            self.execution_context.context["session"].close()
