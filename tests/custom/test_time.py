from datetime import time

from sqlalchemy_to_json_schema.custom.format import validate_time


def _callFUT(*args, **kwargs):
    return validate_time(*args, **kwargs)


def test_it1():
    now = time(10, 20, 30).isoformat() + "Z"
    result = _callFUT(now)
    assert result is True


def test_it2():
    now = time(10, 20, 30).isoformat() + ".809840Z"
    result = _callFUT(now)
    assert result is True


def test_it3():
    now = time(10, 20, 30).isoformat() + ".809840+10:20"
    result = _callFUT(now)
    assert result is True


def test_it4():
    now = time(10, 20, 30).isoformat() + ".809840-10:20"
    result = _callFUT(now)
    assert result is True
