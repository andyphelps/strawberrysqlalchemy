import strawberry

from strawchemy.directives import Lookup


@strawberry.type(directives=[Lookup()])
class SupplierType:
    id: int
    name: str
