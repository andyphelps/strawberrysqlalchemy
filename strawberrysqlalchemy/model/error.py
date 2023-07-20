import strawberry


@strawberry.type
class DatasetError:
    title: str
    description: str


