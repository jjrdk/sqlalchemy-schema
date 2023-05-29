from datetime import date, time
from typing import Optional

from dateutil import parser
from dateutil.parser import ParserError


def parse_date(date_string: str, /) -> Optional[date]:
    try:
        timestamp = parser.isoparse(date_string)
    except ValueError:
        return None

    return timestamp.date()


def validate_date(date_string: str, /) -> bool:
    return parse_date(date_string) is not None


def parse_time(time_string: str, /) -> Optional[time]:
    try:
        timestamp = parser.parse(time_string)
    except ParserError:
        return None

    time_value = timestamp.time()
    time_value = time_value.replace(tzinfo=timestamp.tzinfo)

    return time_value


def validate_time(time_string: str, /) -> bool:
    return parse_time(time_string) is not None
