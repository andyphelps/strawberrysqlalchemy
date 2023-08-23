from dataclasses import dataclass
from typing import List


@dataclass
class SimpleModel:
    id: int
    root_value_1: int
    wibble: str


@dataclass
class NestedModelA1:
    id: int
    blah: List[str]
    loop: List["NestedModel"]


@dataclass
class NestedModelA:
    id: int
    nest: NestedModelA1


@dataclass
class NestedModel:
    id: int
    nest: List[NestedModelA]
