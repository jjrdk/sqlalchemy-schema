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
        actual = transformer.transform([User], 0)

        # Assert
        assert actual == {
            "properties": {},
            "required": ["name", "pk"],
            "title": "User",
            "type": "object",
        }

    def test_transform_module(self, schema_factory: SchemaFactory) -> None:
        # Arrange
        transformer = JSONSchemaTransformer(schema_factory)

        # Act
        actual = transformer.transform([models], 0)

        # Assert
        assert actual == {
            "definitions": {
                "Address": {
                    "properties": {},
                    "required": ["pk", "street", "town"],
                    "title": "Address",
                    "type": "object",
                },
                "Group": {
                    "properties": {},
                    "required": ["name", "pk"],
                    "title": "Group",
                    "type": "object",
                },
                "User": {
                    "properties": {},
                    "required": ["name", "pk"],
                    "title": "User",
                    "type": "object",
                },
            },
        }
