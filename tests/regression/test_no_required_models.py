from sqlalchemy_to_json_schema import SchemaFactory, StructuralWalker
from sqlalchemy_to_json_schema.dictify import ModelLookup, objectify
from tests.fixtures import models


def _callFUT(*args, **kwargs):
    return objectify(*args, **kwargs)


def test_no_required():
    schema_factory = SchemaFactory(StructuralWalker)
    schema = schema_factory(models.MyModel, excludes=["id"])
    modellookup = ModelLookup(models)

    params = {"name": "foo", "value": 1}
    _callFUT(params, schema, modellookup)
