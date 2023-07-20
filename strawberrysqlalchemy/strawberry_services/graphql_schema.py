from typing import List

import strawberry
from strawberry import Schema

from strawberrysqlalchemy.model.entity import Dataset
from strawberrysqlalchemy.strawberry_services.extensions.database_session import DatabaseSessionExtension
from strawberrysqlalchemy.strawberry_services.extensions.error_handler import ErrorHandlerExtension
from strawberrysqlalchemy.strawberry_services.resolvers import (
    get_datasets,
    add_dataset,
    add_datafile_to_dataset,
)


@strawberry.type
class Query:
    get_datasets: List[Dataset] = get_datasets


@strawberry.type
class Mutation:
    add_dataset: Dataset = add_dataset
    add_datafile_to_dataset: Dataset = add_datafile_to_dataset


schema: Schema = Schema(
    query=Query,
    mutation=Mutation,
    extensions=[DatabaseSessionExtension, ErrorHandlerExtension]
)
