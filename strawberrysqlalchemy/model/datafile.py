import strawberry

from strawberrysqlalchemy.model.supplier import Supplier


@strawberry.type
class Datafile:
    id: int
    name: str
    produced_by: Supplier