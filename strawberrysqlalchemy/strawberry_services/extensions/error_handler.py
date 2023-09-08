from typing import Any, Callable

from graphql import GraphQLResolveInfo
from strawberry.extensions import SchemaExtension
from strawberry.utils.await_maybe import AwaitableOrValue

from strawberrysqlalchemy.model.error import DatasetError


class ErrorHandlerExtension(SchemaExtension):

    def resolve(
            self,
            _next: Callable,
            root: Any,
            info: GraphQLResolveInfo,
            *args: str,
            **kwargs: Any,
    ) -> AwaitableOrValue[object]:
        try:
            response = _next(root, info, *args, **kwargs)
            return response
        except DatasetError as dex:
            raise dex
        except Exception as ex:
            raise DatasetError("An unhandled error occurred")
