from typing import Optional

import strawberry

from model.supplier_type import SupplierType
from strawchemy.directives import Lookup


@strawberry.type(directives=[Lookup()])
class Supplier:
    id: int
    name: str
    address: str
    main_contact: str
    main_phone_number: Optional[str]
    supplier_type: SupplierType
