from unittest.mock import ANY

import pytest

from sqlalchemy_to_json_schema import SchemaFactory
from sqlalchemy_to_json_schema.command.transformer import JSONSchemaTransformer
from sqlalchemy_to_json_schema.walkers import StructuralWalker
from tests.fixtures import models
from tests.fixtures.models.user import User


@pytest.fixture
def schema_factory() -> SchemaFactory:
    return SchemaFactory(StructuralWalker)


class TestJSONSchemaTransformer:
    def test_transform_model(self, schema_factory: SchemaFactory) -> None:
        # Arrange
        transformer = JSONSchemaTransformer(schema_factory)

        # Act
        actual = transformer.transform([User], None)

        # Assert
        assert actual == {
            "definitions": {"Address": ANY, "Group": ANY},
            "properties": {
                "address": {"$ref": "#/definitions/Address"},
                "created_at": {"format": "date-time", "type": "string"},
                "group": {"$ref": "#/definitions/Group"},
                "name": {"maxLength": 255, "type": "string"},
                "pk": {"description": "primary key", "type": "integer"},
            },
            "required": ["name", "pk"],
            "title": "User",
            "type": "object",
        }

    def test_transform_module(self, schema_factory: SchemaFactory) -> None:
        # Arrange
        transformer = JSONSchemaTransformer(schema_factory)

        # Act
        actual = transformer.transform([models], None)

        # Assert
        assert actual == {
            "definitions": {
                "Address": {
                    "properties": ANY,
                    "required": ["pk", "street", "town"],
                    "title": "Address",
                    "type": "object",
                },
                "Group": {
                    "properties": ANY,
                    "required": ["name", "pk"],
                    "title": "Group",
                    "type": "object",
                },
                "User": {
                    "properties": ANY,
                    "required": ["name", "pk"],
                    "title": "User",
                    "type": "object",
                },
            },
        }
