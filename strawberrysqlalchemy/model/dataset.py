from typing import List

import strawberry

from strawberrysqlalchemy.model.crs import Crs
from strawberrysqlalchemy.model.datafile import Datafile


@strawberry.type
class Dataset:
    id: int
    name: str
    datafiles: List[Datafile]
    crs: Crs
