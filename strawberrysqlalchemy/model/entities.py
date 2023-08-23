from dataclasses import dataclass
from typing import List


@dataclass
class Datafile:
    id: int
    name: str


@dataclass
class Dataset:
    id: int
    name: str
    datafiles: List[Datafile]
    main_datafile: Datafile
