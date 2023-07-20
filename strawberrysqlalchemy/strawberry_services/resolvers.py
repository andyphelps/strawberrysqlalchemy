from typing import Optional, List, cast, Set

import strawberry
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session, joinedload
from strawberry.types import Info

from strawberrysqlalchemy.model.entity import Dataset, DatafileInput, Datafile
from strawberrysqlalchemy.model.error import DatasetError
from strawberrysqlalchemy.model.input import DatasetInput, PageInfoInput
from strawberrysqlalchemy.strawberry_services.helpers import expand_selected_fields


@strawberry.field
def get_datasets(
        info: Info,
        id: Optional[int] = None,
        ids: Optional[List[int]] = None,
        page_info: Optional[PageInfoInput] = None
) -> List[Dataset]:
    session: Session = info.context["session"]
    select_clause = select(Dataset)

    selected_fields: List[str] = expand_selected_fields(info.selected_fields)

    if any("/datafiles/" in field for field in selected_fields):
        select_clause = select_clause.options(joinedload(Dataset.datafiles))  # noqa

    if id:
        statement = select_clause.where(Dataset.id == id)  # noqa
    elif ids:
        statement = select_clause.where(Dataset.id.in_(ids))  # noqa
    else:
        statement = select_clause

    if page_info:
        statement = statement.offset((page_info.page - 1) * page_info.page_size).limit(page_info.page_size)

    response: List[Dataset] = cast(List[Dataset], session.scalars(statement).unique().all())

    if id and not response:
        raise DatasetError(f"Id: {id} not found")

    if ids and len(ids) != len(response):
        missing_ids: Set[int] = set(ids) - {dataset.id for dataset in response}
        raise DatasetError(f"Ids: {list(missing_ids)} not found")

    print(f"{len(response)} rows returned")

    return response


@strawberry.mutation
def add_dataset(info: Info, dataset_input: DatasetInput) -> Dataset:
    session: Session = info.context["session"]

    new_dataset = Dataset.from_partial(dataset_input)
    session.add(new_dataset)
    session.commit()
    session.refresh(new_dataset)

    return new_dataset


@strawberry.mutation
def add_datafile_to_dataset(info: Info, dataset_id: int, datafile_input: DatafileInput) -> Dataset:
    session: Session = info.context["session"]

    try:
        dataset: Dataset = session.scalars(select(Dataset).where(Dataset.id == dataset_id)).unique().one()  # noqa
    except NoResultFound:
        raise DatasetError(f"Could not find Dataset with id: {dataset_id}")

    dataset.datafiles.append(Datafile.from_partial(datafile_input))
    session.commit()
    session.refresh(dataset)

    return dataset
