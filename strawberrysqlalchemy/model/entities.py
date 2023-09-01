from dataclasses import dataclass
from enum import Enum
from typing import List


@dataclass
class Datafile:
    id: int
    name: str


@dataclass
class Crs:
    id: int
    name: str


@dataclass
class Dataset:
    id: int
    name: str
    datafiles: List[Datafile]
    crs: Crs
