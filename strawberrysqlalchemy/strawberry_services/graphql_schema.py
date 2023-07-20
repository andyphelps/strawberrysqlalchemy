import strawberry
from strawberry import Schema

from strawberrysqlalchemy.strawberry_services.database_session_extension import DatabaseSessionExtension
from strawberrysqlalchemy.strawberry_services.resolvers import (
    DatasetsResponse,
    get_datasets,
    DatasetResponse,
    add_dataset,
    add_datafile_to_dataset,
)


@strawberry.type
class Query:
    get_datasets: DatasetsResponse = get_datasets


@strawberry.type
class Mutation:
    add_dataset: DatasetResponse = add_dataset
    add_datafile_to_dataset: DatasetResponse = add_datafile_to_dataset


schema: Schema = Schema(query=Query, mutation=Mutation, extensions=[DatabaseSessionExtension])
