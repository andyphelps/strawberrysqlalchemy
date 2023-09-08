import pkgutil
from types import ModuleType
from typing import Set, Type

from strawberry import Schema

from strawberrysqlalchemy.model.entities import Datafile, Dataset, Crs


def discover_model_classes(schema: Schema) -> Set[Type]:
    types = schema.schema_converter.type_map
    ...
# def discover_model_dataclasses(model_package_name: str) -> Set[type]:
#     # model_package: ModuleType = pkgutil.resolve_name(model_package_name)
#     #
#     # model_modules: Set[ModuleType] = {
#     #     pkgutil.resolve_name(module_info.name) for module_info in
#     #     pkgutil.walk_packages(model_package.__path__, prefix=f"{model_package.__name__}.")
#     #     if not module_info.ispkg
#     # }
#
#     return {
#         Dataset, Datafile, Crs
#     }
#     # return {
#     #     x[1]
#     #     for x in chain.from_iterable(inspect.getmembers(module, dataclasses.is_dataclass)
#     #                                  for module in model_modules)
#     # }
