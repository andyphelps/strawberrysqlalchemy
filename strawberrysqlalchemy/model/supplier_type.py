from typing import List

import strawberry

from strawberrysqlalchemy.model.crs import Crs


@strawberry.type
class SupplierType:
    id: int
    name: str
