import uvicorn
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from strawberrysqlalchemy.strawberry_services.graphql_schema import schema

graphql_app: GraphQLRouter = GraphQLRouter(schema)

app: FastAPI = FastAPI()
app.include_router(graphql_app, prefix="/graphql")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
