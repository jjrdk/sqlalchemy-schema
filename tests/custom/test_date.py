from datetime import date

from sqlalchemy_to_json_schema.custom.format import validate_date


def _callFUT(*args, **kwargs):
    return validate_date(*args, **kwargs)


def test_it():
    print(date.today().isoformat())
    today = date.today().isoformat()
    result = _callFUT(today)
    assert result is True


def test_it__failure():
    today = "2011-13-13"
    result = _callFUT(today)
    assert result is False


def test_it__failure2():
    today = "2011/12/12"
    result = _callFUT(today)
    assert result is False
