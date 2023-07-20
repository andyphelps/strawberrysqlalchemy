from typing import List, Union

import strawberry

from strawberrysqlalchemy.model.entity import Dataset
from strawberrysqlalchemy.model.error import DatasetError


@strawberry.type
class Datasets:
    datasets: List[Dataset]


DatasetsResponse = Union[Datasets, DatasetError]
DatasetResponse = Union[Dataset, DatasetError]
