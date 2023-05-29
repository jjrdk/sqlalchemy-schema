import os.path
from collections import OrderedDict

import pytest
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base

from sqlalchemy_to_json_schema import SchemaFactory, StructuralWalker

# using sqlalchemy's automap


@pytest.fixture(scope="module")
def db():
    dbname = os.path.join(os.path.abspath(os.path.dirname(__file__)), "reflection.db")
    engine = create_engine(f"sqlite:///{dbname}")
    Base = automap_base()
    Base.prepare(engine, reflect=True)
    return Base


def _getTarget():
    return SchemaFactory


def _makeOne(*args, **kwargs):
    return _getTarget()(StructuralWalker)


def test_it(db):
    target = _makeOne()
    schema = target(db.classes.artist)
    expected = {
        "title": "artist",
        "properties": OrderedDict(
            [
                ("artistid", {"type": "integer"}),
                ("artistname", {"type": "string"}),
                (
                    "track_collection",
                    {"items": {"$ref": "#/definitions/track"}, "type": "array"},
                ),
            ]
        ),
        "definitions": {
            "track": {
                "properties": OrderedDict(
                    [
                        ("trackid", {"type": "integer"}),
                        ("trackname", {"type": "string"}),
                    ]
                ),
                "required": ["trackid"],
                "type": "object",
            }
        },
        "type": "object",
        "required": ["artistid", "artistname"],
    }
    assert schema == expected


def test_it2(db):
    target = _makeOne()
    schema = target(db.classes.track)
    expected = {
        "title": "track",
        "properties": OrderedDict(
            [
                ("trackid", {"type": "integer"}),
                ("trackname", {"type": "string"}),
                ("artist", {"$ref": "#/definitions/artist"}),
            ]
        ),
        "definitions": {
            "artist": {
                "properties": OrderedDict(
                    [
                        ("artistid", {"type": "integer"}),
                        ("artistname", {"type": "string"}),
                    ]
                ),
                "required": ["artistid", "artistname"],
                "type": "object",
            }
        },
        "type": "object",
        "required": ["trackid"],
    }
    assert schema == expected
