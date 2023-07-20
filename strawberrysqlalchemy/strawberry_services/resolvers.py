from typing import Optional, List

import strawberry
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from strawberry.types import Info

from strawberrysqlalchemy.model.entity import Dataset, DatafileInput, Datafile
from strawberrysqlalchemy.model.input import DatasetInput, PageInfo
from strawberrysqlalchemy.model.return_type import DatasetsResponse, DatasetResponse, Datasets
from strawberrysqlalchemy.strawberry_services.helpers import expand_selected_fields


@strawberry.field
def get_datasets(
        info: Info,
        id: Optional[int] = None,
        ids: Optional[List[int]] = None,
        page_info: Optional[PageInfo] = None
) -> DatasetsResponse:
    session: Session = info.context["session"]
    select_clause = select(Dataset)

    selected_fields: List[str] = expand_selected_fields(info.selected_fields)

    if any("/datasets/datafiles/" in field for field in selected_fields):
        select_clause = select_clause.options(joinedload(Dataset.datafiles))

    if id:
        statement = select_clause.where(Dataset.id == id)  # noqa
    elif ids:
        statement = select_clause.where(Dataset.id.in_(ids))  # noqa
    else:
        statement = select_clause

    if page_info:
        statement = statement.offset((page_info.page-1) * page_info.page_size).limit(page_info.page_size)
        
    response: Datasets = Datasets(datasets=session.scalars(statement).unique().all())
    print(f"{len(response.datasets)} rows returned")

    return response


@strawberry.mutation
def add_dataset(info: Info, dataset_input: DatasetInput) -> DatasetResponse:
    session: Session = info.context["session"]

    new_dataset = Dataset.from_partial(dataset_input)
    session.add(new_dataset)
    session.commit()
    session.refresh(new_dataset)

    return new_dataset


@strawberry.mutation
def add_datafile_to_dataset(info: Info, dataset_id: int, datafile_input: DatafileInput) -> DatasetResponse:
    session: Session = info.context["session"]

    dataset: Dataset = session.scalars(select(Dataset).where(Dataset.id == dataset_id)).unique().one()  # noqa
    dataset.datafiles.append(Datafile.from_partial(datafile_input))
    session.commit()
    session.refresh(dataset)

    return dataset
