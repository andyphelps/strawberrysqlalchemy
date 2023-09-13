from typing import List, Optional

import strawberry

from model.crs import Crs
from model.datafile import Datafile


@strawberry.type
class Dataset:
    id: int
    name: str
    datafiles: List[Datafile]
    last_datafile: Optional[Datafile]
    crs: Crs


@strawberry.type
class SimpleDataset:
    id: int
    name: str
    datafiles: List[Datafile]


@strawberry.type
class OptionalDataset:
    id: int
    name: str
    last_datafile: Optional[Datafile]


@strawberry.type
class NoIdDataset:
    name: str


@strawberry.type
class NotIntIdDataset:
    id: float
    name: str


@strawberry.type
class ListOptionalDataset:
    id: int
    name: str
    last_datafile: List[Optional[Datafile]]


@strawberry.type
class OptionalListDataset:
    id: int
    name: str
    last_datafile: Optional[List[Datafile]]
