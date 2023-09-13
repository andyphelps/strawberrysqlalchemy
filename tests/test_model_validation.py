from typing import List

import pytest

from model.dataset import (
    SimpleDataset,
    OptionalDataset,
    NoIdDataset,
    NotIntIdDataset,
    ListOptionalDataset,
    OptionalListDataset,
)
from model.supplier import Supplier
from model.supplier_type import SupplierType
from strawchemy.model_validation import validate_model_classes


class TestModelValidation:

    def test_when_valid_model_then_passes_validation(self) -> None:
        validate_model_classes([Supplier, SupplierType])

    @pytest.mark.parametrize(
        argnames=["type_list", "error_text"],
        argvalues=[
            ([NoIdDataset], "Type NoIdDataset does not define an 'id' member of type 'int'"),
            ([NotIntIdDataset], "Type NotIntIdDataset does not define an 'id' member of type 'int'"),
            ([Supplier], "Type Supplier has field with a disallowed "
                         "type 'SupplierType' on field 'supplier_type'"),
            ([SimpleDataset], "Type SimpleDataset has a list field with a disallowed "
                              "type 'Datafile' on field 'datafiles'"),
            ([OptionalDataset], "Type OptionalDataset has an optional field with a disallowed "
                                "type 'Datafile' on field 'last_datafile'"),
            ([ListOptionalDataset], "Type ListOptionalDataset has a list of optional or a optional of list "
                                    "type on field 'last_datafile' with type 'Datafile' "
                                    "and nesting these types isn't allowed"),
            ([OptionalListDataset], "Type OptionalListDataset has a list of optional or a optional of list "
                                    "type on field 'last_datafile' with type 'Datafile' "
                                    "and nesting these types isn't allowed"),
        ],
        ids=[
            "Id not present",
            "Id not int",
            "Child type missing",
            "Child list type missing",
            "Child optional type missing",
            "List of Optional type",
            "Optional of List type",
        ])
    def test_failures_on_model_validation(self, type_list: List[type], error_text: str) -> None:
        with pytest.raises(AttributeError) as err:
            validate_model_classes(type_list)

        assert err.match(error_text)
