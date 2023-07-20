from typing import List, Optional, TypeVar, Any

import strawberry
from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import registry, relationship

from strawberrysqlalchemy.model.input import DatafileInput, DatasetInput

reg = registry()


class LoadableFromPartial:
    @classmethod
    def from_partial(cls, data: Any) -> "LoadableFromPartial":
        if issubclass(cls, type(data)):
            return cls(**data.__dict__)  # noqa
        else:
            raise RuntimeError(f"Cannot create {cls} from {data} ")


# A dual-purpose model is used here.  These classes define a strawberry class as well as a sqlalchemy class
@reg.mapped
@strawberry.type
class Datafile(DatafileInput, LoadableFromPartial):
    __table__ = Table(
        "datafile",
        reg.metadata,
        Column("id", Integer, primary_key=True),
        Column("dataset_id", Integer, ForeignKey("dataset.id"), nullable=False),
        Column("filename", String(255), nullable=False),
        Column("uri", String(255), nullable=False),
    )

    __mapper_args__ = {
        "properties": {
            "dataset": relationship("Dataset", back_populates="datafiles")
        }
    }

    id: int = strawberry.field(default=None)
    dataset_id: int = strawberry.field(default=None)
    dataset: "Dataset" = strawberry.field(default=None)


@reg.mapped
@strawberry.type
class Dataset(DatasetInput, LoadableFromPartial):
    __table__ = Table(
        "dataset",
        reg.metadata,
        Column("id", Integer, primary_key=True),
        Column("name", String(50), nullable=False),
        Column("retrieval_uri", String(255), nullable=False)
    )

    __mapper_args__ = {
        "properties": {
            "datafiles": relationship("Datafile", back_populates="dataset", cascade="all, delete-orphan")
        }
    }

    id: int = strawberry.field(default=None)
    datafiles: List[Datafile] = strawberry.field(default_factory=list)
