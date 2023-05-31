r"""
jsondict <-> dict <-> model object
   \______________________/
"""
import json
from datetime import datetime

import pytz
from jsonschema import Draft4Validator

import tests.fixtures.models as models
from sqlalchemy_to_json_schema import SchemaFactory
from sqlalchemy_to_json_schema.mapping import MappingFactory
from sqlalchemy_to_json_schema.walkers import StructuralWalker

from .fixtures.models import Group, User


def _datetime(*args):
    args = list(args)
    args.append(pytz.utc)
    return datetime(*args)


def _makeOne(schema_factory, model, *args, **kwargs):
    module = models
    mapping_factory = MappingFactory(Draft4Validator, schema_factory, module, *args, **kwargs)
    return mapping_factory(model)


def test_it__dict_from_model_object():
    schema_factory = SchemaFactory(StructuralWalker)
    target = _makeOne(schema_factory, Group)

    group = Group(name="ravenclaw", color="blue", created_at=_datetime(2000, 1, 1, 10, 0, 0, 0))
    group.users = [User(name="foo", created_at=_datetime(2000, 1, 1, 10, 0, 0, 0))]

    group_dict = target.dict_from_object(group)
    assert group_dict == {
        "color": "blue",
        "users": [
            {
                "created_at": _datetime(2000, 1, 1, 10, 0, 0, 0),
                "pk": None,
                "name": "foo",
            }
        ],
        "created_at": _datetime(2000, 1, 1, 10, 0, 0, 0),
        "pk": None,
        "name": "ravenclaw",
    }


def test_it__jsondict_from_model():
    schema_factory = SchemaFactory(StructuralWalker)
    target = _makeOne(schema_factory, Group)

    group = Group(name="ravenclaw", color="blue", created_at=_datetime(2000, 1, 1, 10, 0, 0, 0))
    group.users = [User(name="foo", created_at=_datetime(2000, 1, 1, 10, 0, 0, 0))]

    jsondict = target.jsondict_from_object(group, verbose=True)

    assert json.dumps(jsondict)

    assert jsondict == {
        "color": "blue",
        "name": "ravenclaw",
        "users": [{"name": "foo", "pk": None, "created_at": "2000-01-01T10:00:00+00:00"}],
        "pk": None,
        "created_at": "2000-01-01T10:00:00+00:00",
    }


def test_it__validate__jsondict():
    schema_factory = SchemaFactory(StructuralWalker)
    target = _makeOne(schema_factory, Group)

    jsondict = {
        "color": "blue",
        "name": "ravenclaw",
        "users": [{"name": "foo", "pk": 1, "created_at": "2000-01-01T10:00:00+00:00"}],
        "pk": 1,
        "created_at": "2000-01-01T10:00:00+00:00",
    }

    target.validate_jsondict(jsondict)


def test_it__dict_from_jsondict():
    schema_factory = SchemaFactory(StructuralWalker)
    target = _makeOne(schema_factory, Group)

    jsondict = {
        "color": "blue",
        "name": "ravenclaw",
        "users": [{"name": "foo", "pk": 10, "created_at": "2000-01-01T10:00:00+00:00"}],
        "pk": None,
        "created_at": "2000-01-01T10:00:00+00:00",
    }

    group_dict = target.dict_from_jsondict(jsondict)

    assert group_dict == {
        "color": "blue",
        "users": [{"created_at": _datetime(2000, 1, 1, 10, 0, 0, 0), "pk": 10, "name": "foo"}],
        "created_at": _datetime(2000, 1, 1, 10, 0, 0, 0),
        "pk": None,
        "name": "ravenclaw",
    }


def test_it__object_from_dict():
    schema_factory = SchemaFactory(StructuralWalker)
    target = _makeOne(schema_factory, Group)

    group_dict = {
        "color": "blue",
        "users": [
            {
                "created_at": _datetime(2000, 1, 1, 10, 0, 0, 0),
                "pk": None,
                "name": "foo",
            }
        ],
        "created_at": _datetime(2000, 1, 1, 10, 0, 0, 0),
        "pk": None,
        "name": "ravenclaw",
    }

    group = target.object_from_dict(group_dict, strict=False)

    assert isinstance(group, Group)
    assert group.color == "blue"
    assert group.name == "ravenclaw"
    assert group.pk is None
    assert group.created_at == _datetime(2000, 1, 1, 10, 0, 0, 0)

    assert (len(group.users) == 1) and (isinstance(group.users[0], User))
    assert group.users[0].name == "foo"
    assert group.users[0].pk is None
    assert group.users[0].created_at == _datetime(2000, 1, 1, 10, 0, 0, 0)
