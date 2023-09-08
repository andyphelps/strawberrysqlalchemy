import strawberry

from strawberrysqlalchemy.model.supplier_type import SupplierType


@strawberry.type
class Supplier:
    id: int
    name: str
    address: str
    main_contact: str
    main_phone_number: str
    supplier_type: SupplierType
