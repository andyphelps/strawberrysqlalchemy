from typing import List, cast

import uvicorn
from fastapi import FastAPI
from sqlalchemy import create_engine
from strawberry.fastapi import GraphQLRouter
from strawberry.schema import BaseSchema

from strawberrysqlalchemy.model.entities import Dataset, Datafile
from strawberrysqlalchemy.strawchemy import StrawchemySchema

engine = create_engine("sqlite://", echo=True)

graphql_app: GraphQLRouter = GraphQLRouter(cast(BaseSchema, StrawchemySchema(queriable_types={Dataset, Datafile},
                                                                             mutable_types={Dataset, Datafile},
                                                                             engine=engine)))

app: FastAPI = FastAPI()
app.include_router(graphql_app, prefix="/graphql")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
