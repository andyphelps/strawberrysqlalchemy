import strawberry

from strawchemy.directives import Lookup


@strawberry.type(directives=[Lookup()])
class Crs:
    id: int
    name: str
