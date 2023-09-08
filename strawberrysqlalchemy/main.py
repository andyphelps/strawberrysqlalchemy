from typing import List, Optional

import strawberry
import uvicorn
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from strawberrysqlalchemy.model.dataset import Dataset
from strawberrysqlalchemy.strawchemy.strawchemy_manager import StrawchemyManager


@strawberry.type
class Query:
    FetchAllDatasets: List[Dataset]
    FetchDatasetById: Optional[Dataset]


@strawberry.type
class Mutation:
    CreateDataset: Dataset
    UpdateDataset: Dataset
    DeleteDataset: Dataset


strawchemy_manager = StrawchemyManager(engine="sqlite:///sqlite.db", query=Query, mutation=Mutation)
graphql_app: GraphQLRouter = GraphQLRouter(schema=strawchemy_manager.schema)

app: FastAPI = FastAPI()
app.include_router(graphql_app, prefix="/graphql")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
