from types import ModuleType
from typing import Sequence
from unittest.mock import ANY

import pytest
from pytest_unordered import unordered
from sqlalchemy.ext.declarative import DeclarativeMeta

from sqlalchemy_to_json_schema import SchemaFactory
from sqlalchemy_to_json_schema.command.transformer import (
    JSONSchemaTransformer,
    collect_models,
)
from sqlalchemy_to_json_schema.walkers import StructuralWalker
from tests import fixtures
from tests.fixtures import models
from tests.fixtures.models.address import Address
from tests.fixtures.models.user import Group, User


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


class TestCollectModels:
    @pytest.mark.parametrize(
        "module, expected",
        [
            pytest.param(fixtures.models.user, [User, Group], id="single model"),
            pytest.param(fixtures.models.not_a_sa_model, [], id="not a model"),
            pytest.param(fixtures.models, [User, Group, Address], id="__all__"),
            pytest.param(lambda x: x, [], id="function"),
        ],
    )
    def test_collect_models(self, module: ModuleType, expected: Sequence[DeclarativeMeta]) -> None:
        """
        ARRANGE given a list of modules
        ACT call the collect_models()
        ASSERT the resulting list of models matches the expected list of models
        """
        # Act
        actual = collect_models(module)

        # Assert
        assert list(actual) == unordered(expected)
