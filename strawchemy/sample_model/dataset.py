from typing import List, Optional

import strawberry

from .crs import Crs
from .datafile import Datafile


@strawberry.type
class Dataset:
    id: int
    name: str
    datafiles: List[Datafile]
    last_datafile: Optional[Datafile]
    crs: Crs
