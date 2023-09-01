import uvicorn
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from strawberrysqlalchemy.strawchemy.strawchemy_manager import StrawchemyManager

strawchemy_manager = StrawchemyManager(engine="sqlite:///", model_package_name="strawberrysqlalchemy.model")

graphql_app: GraphQLRouter = GraphQLRouter(schema=strawchemy_manager.schema)

app: FastAPI = FastAPI()
app.include_router(graphql_app, prefix="/graphql")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
