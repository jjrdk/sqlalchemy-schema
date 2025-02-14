from datetime import date, time
from typing import Optional

import pytest
from dateutil import tz

from sqlalchemy_schema.utils.format import (
    parse_date,
    parse_time,
    validate_date,
    validate_time,
)


@pytest.mark.parametrize(
    "date_string, expected",
    [
        # Truthy values
        pytest.param("2021-01-01", date(2021, 1, 1)),
        pytest.param("2021-02-28", date(2021, 2, 28)),
        pytest.param("20210101", date(2021, 1, 1)),
        # Falsy values
        pytest.param("2021/01/01", None),
        pytest.param("2021-01-32", None),
        pytest.param("2021-02-29", None),
        pytest.param("2021-13-01", None),
    ],
)
def test_parse_date(date_string: str, expected: Optional[date]) -> None:
    """
    ARRANGE prepare the input date_string
    ACT call the `parse_date` function with the date_string
    ASSERT check if the output matches the expected value
    """
    assert parse_date(date_string) == expected


@pytest.mark.parametrize(
    "date_string, expected",
    [
        # Truthy values
        pytest.param("2021-01-01", True),
        pytest.param("20210101", True),
        pytest.param("2021-02-28", True),
        # Falsy values
        pytest.param("2021/01/01", False),
        pytest.param("2021-01-32", False),
        pytest.param("2021-02-29", False),
        pytest.param("2021-13-01", False),
    ],
)
def test_validate_date(date_string: str, expected: Optional[date]) -> None:
    """
    ARRANGE prepare the input date_string
    ACT call the `validate_date` function with the date_string
    ASSERT check if the output matches the expected value
    """
    assert validate_date(date_string) == expected


@pytest.mark.parametrize(
    "time_string, expected",
    [
        # Truthy values
        pytest.param("00:00:00", time(0, 0, 0)),
        pytest.param(
            "12:34:56.789-03", time(12, 34, 56, 789000, tzinfo=tz.tzoffset(None, -10800))
        ),
        pytest.param("12:34:56.789", time(12, 34, 56, 789000)),
        pytest.param("12:34:56.789+03", time(12, 34, 56, 789000, tzinfo=tz.tzoffset(None, 10800))),
        pytest.param(
            "12:34:56.789Z-03", time(12, 34, 56, 789000, tzinfo=tz.tzoffset(None, 10800))
        ),
        pytest.param("12:34:56.789Z", time(12, 34, 56, 789000, tzinfo=tz.UTC)),
        pytest.param(
            "12:34:56.789Z+03", time(12, 34, 56, 789000, tzinfo=tz.tzoffset(None, -10800))
        ),
        pytest.param("12:34:56", time(12, 34, 56)),
        pytest.param("12:34:56Z", time(12, 34, 56, tzinfo=tz.UTC)),
        pytest.param("12:34", time(12, 34)),
        pytest.param("23:59:59", time(23, 59, 59)),
        # Falsy values
        pytest.param("12:34:56:789", None),
        pytest.param("invalid_time", None),
    ],
)
def test_parse_time(time_string: str, expected: Optional[time]) -> None:
    """
    ARRANGE given a time as string
    ACT call the `parse_time` function
    ASSERT returns the expected
    """
    # act
    actual = parse_time(time_string)

    # assert
    assert actual == expected


@pytest.mark.parametrize(
    "time_string, expected",
    [
        # Truthy values
        pytest.param("00:00:00", True),
        pytest.param("12:34:56.789-03", True),
        pytest.param("12:34:56.789", True),
        pytest.param("12:34:56.789+03", True),
        pytest.param("12:34:56.789Z-03", True),
        pytest.param("12:34:56.789Z", True),
        pytest.param("12:34:56.789Z+03", True),
        pytest.param("12:34:56", True),
        pytest.param("12:34:56Z", True),
        pytest.param("12:34", True),
        pytest.param("23:59:59", True),
        # Falsy values
        pytest.param("12:34:56:789", False),
        pytest.param("invalid_time", False),
    ],
)
def test_validate_time(time_string: str, expected: bool) -> None:
    """
    ARRANGE given a time as string
    ACT call the `validate_time` function
    ASSERT returns the expected
    """
    # act
    actual = validate_time(time_string)

    # assert
    assert actual == expected
