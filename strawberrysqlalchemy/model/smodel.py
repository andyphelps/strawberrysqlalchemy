import inspect
import typing
from typing import Type, Any, List

import strawberry
import dataclasses
import ast

from strawberry.types.types import StrawberryObjectDefinition
from entity import Dataset as OldDataset
from strawberrysqlalchemy import strawchemy


@strawberry.input
class DatafileInput:
    filename: str
    uri: str


@strawchemy.type
class Datafile(DatafileInput):
    # __table__ = Table(
    #     "datafile",
    #     reg.metadata,
    #     Column("id", Integer, primary_key=True),
    #     Column("dataset_id", Integer, ForeignKey("dataset.id"), nullable=False),
    #     Column("filename", String(255), nullable=False),
    #     Column("uri", String(255), nullable=False),
    # )
    #
    # __mapper_args__ = {
    #     "properties": {
    #         "dataset": relationship("Dataset", back_populates="datafiles")
    #     }
    # }

    ...


@strawberry.input
class DatasetInput:
    name: str
    retrieval_uri: str


@strawchemy.type(1)
class Dataset(DatasetInput):
    # __table__ = Table(
    #     "dataset",
    #     reg.metadata,
    #     Column("id", Integer, primary_key=True),
    #     Column("name", String(50), nullable=False),
    #     Column("retrieval_uri", String(255), nullable=False)
    # )
    #
    # __mapper_args__ = {
    #     "properties": {
    #         "datafiles": relationship("Datafile", back_populates="dataset", cascade="all, delete-orphan")
    #     }
    # }

    datafiles: List[Datafile]


if __name__ == "__main__":
    ds = Dataset(datafiles=[Datafile(filename="wibble.txt", uri="flibble")], retrieval_uri=None,
                 name="wibble")
    pass
