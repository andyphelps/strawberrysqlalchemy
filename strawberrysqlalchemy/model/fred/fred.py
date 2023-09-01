from dataclasses import dataclass
from typing import List

from strawberrysqlalchemy.model.entities import Crs


@dataclass
class Fred:
    id: int
    wibble: int
    wobble: List[Crs]
