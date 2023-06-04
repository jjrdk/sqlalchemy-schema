import pprint
from datetime import datetime

from sqlalchemy_to_json_schema import SchemaFactory
from sqlalchemy_to_json_schema.dictify import dictify, prepare
from sqlalchemy_to_json_schema.walkers import StructuralWalker
from tests.fixtures.models import Group, User


def _callFUT(*args, **kwargs):
    return dictify(*args, **kwargs)


def _callFUT3(*args, **kwargs):
    return prepare(*args, **kwargs)


def test_it__dictify():
    factory = SchemaFactory(StructuralWalker)
    group_schema = factory(Group)

    created_at = datetime(2000, 1, 1)
    users = [
        User(name="foo", created_at=created_at),
        User(name="boo", created_at=created_at),
    ]
    group = Group(name="ravenclaw", color="blue", users=users, created_at=created_at)

    result = _callFUT(group, group_schema)
    assert result == {
        "pk": None,
        "color": "blue",
        "name": "ravenclaw",
        "created_at": created_at,
        "users": [
            {"pk": None, "name": "foo", "created_at": created_at},
            {"pk": None, "name": "boo", "created_at": created_at},
        ],
    }


def test_it__dictify2():
    factory = SchemaFactory(StructuralWalker)
    user_schema = factory(User)

    created_at = datetime(2000, 1, 1)
    group = Group(name="ravenclaw", color="blue", created_at=created_at)
    user = User(name="foo", created_at=created_at, group=group)

    result = _callFUT(user, user_schema)
    pprint.pprint(result)
    assert result == {
        "pk": None,
        "name": "foo",
        "created_at": created_at,
        "group": {
            "pk": None,
            "color": "blue",
            "name": "ravenclaw",
            "created_at": created_at,
        },
    }


def test_it__prepare():
    factory = SchemaFactory(StructuralWalker)
    group_schema = factory(Group)
    group_dict = {
        "name": "ravenclaw",
        "created_at": "2000-01-01T00:00:00+00:00",
        "color": "blue",
        "pk": 1,
        "users": [
            {"name": "foo", "created_at": "2000-01-01T00:00:00+00:00", "pk": 12},
            {"name": "boo", "created_at": "2000-01-01T00:00:00+00:00", "pk": 13},
        ],
    }

    result = _callFUT3(group_dict, group_schema)
    assert result == {
        "name": "ravenclaw",
        "created_at": "2000-01-01T00:00:00+00:00",
        "color": "blue",
        "pk": 1,
        "users": [
            {"name": "foo", "created_at": "2000-01-01T00:00:00+00:00", "pk": 12},
            {"name": "boo", "created_at": "2000-01-01T00:00:00+00:00", "pk": 13},
        ],
    }


def test_it__prepare_partial():
    factory = SchemaFactory(StructuralWalker)
    group_schema = factory(Group)
    group_dict = {"name": "ravenclaw", "color": "blue", "pk": 1}

    result = _callFUT3(group_dict, group_schema)
    assert result == {"name": "ravenclaw", "pk": 1, "color": "blue", "users": []}
