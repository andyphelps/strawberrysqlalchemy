from itertools import chain
from typing import List

from strawberry.types.nodes import SelectedField, Selection


def expand_selected_fields(selected_fields: List[Selection], prefix: str = "/") -> List[str]:
    return (
            [  # Add paths for leaf selections
                prefix + selection.name
                for selection in selected_fields
                if isinstance(selection, SelectedField) and not selection.selections
            ] +
            list(  # Recurse over child selections, flatten, and add to list
                chain.from_iterable(
                    expand_selected_fields(
                        selection.selections,
                        prefix + getattr(selection, "name", getattr(selection, "type_condition", "?")) + "/"
                    )
                    for selection in selected_fields
                    if selection.selections
                ))
    )
