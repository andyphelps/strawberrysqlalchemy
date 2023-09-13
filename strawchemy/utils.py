import re


def snake_it(value: str) -> str:
    return re.sub(r"(?<!^)(?<!_)(?=[A-Z])", "_", value).lower()
