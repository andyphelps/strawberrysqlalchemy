from datetime import datetime, date, time
from typing import Dict, Type, TypeVar

from sqlalchemy import Integer, Float, String, Boolean, DateTime, Date, Time

T = TypeVar("T")

MAPPED_TYPES: Dict[Type, Type[T]] = {
    int: Integer,
    float: Float,
    str: String,
    bool: Boolean,
    datetime: DateTime,
    date: Date,
    time: Time,
}
