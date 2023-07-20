import strawberry


@strawberry.input
class DatafileInput:
    filename: str
    uri: str


@strawberry.input
class DatasetInput:
    name: str
    retrieval_uri: str


@strawberry.input
class PageInfo:
    page_size: int
    page: int

    @property
    def is_paging(self) -> bool:
        return all((self.page, self.page_size))
