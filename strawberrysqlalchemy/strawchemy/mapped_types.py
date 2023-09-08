from datetime import datetime, date, time
from typing import Dict

from sqlalchemy import Integer, Float, String, Boolean, DateTime, Date, Time

MAPPED_TYPES: Dict[type, type] = {
    int: Integer,
    float: Float,
    str: String,
    bool: Boolean,
    datetime: DateTime,
    date: Date,
    time: Time,
}
