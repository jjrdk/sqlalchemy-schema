import jsonschema
import pytest
import sqlalchemy as sa
from jsonschema.exceptions import ValidationError
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy_to_json_schema import SchemaFactory, StructuralWalker
from sqlalchemy_to_json_schema.dictify import jsonify


def _callFUT(*args, **kwargs):
    # see: https://github.com/expobrain/sqlalchemy_to_json_schema/pull/3

    return jsonify(*args, **kwargs)


def _makeSchema(model):
    factory = SchemaFactory(StructuralWalker)
    return factory(model)


def _makeModel():
    Base = declarative_base()

    class UserKey(Base):
        __tablename__ = "user_key"
        key = sa.Column(
            sa.Integer, sa.Sequence("user_id_seq"), primary_key=True, doc="primary key"
        )
        deactivated_at = sa.Column(sa.DateTime(), nullable=True)
        keytype = sa.Column(sa.String(36), nullable=False)

    return UserKey


def test_it():
    UserKey = _makeModel()
    schema = _makeSchema(UserKey)

    uk = UserKey(key=1, keytype="*keytype*")
    d = _callFUT(uk, schema)

    assert "deactivated_at" not in d

    jsonschema.validate(d, schema)


def test_it__validation_failure__when_verbose_is_True():
    UserKey = _makeModel()
    schema = _makeSchema(UserKey)

    uk = UserKey(key=1, keytype="*keytype*")
    d = _callFUT(uk, schema, verbose=True)

    assert d["deactivated_at"] is None

    with pytest.raises(ValidationError):
        jsonschema.validate(d, schema)
