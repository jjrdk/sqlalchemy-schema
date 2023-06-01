from typing import Any, Dict, OrderedDict, Type

import pytest
from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from sqlalchemy_to_json_schema import DefaultClassfier, SchemaFactory
from sqlalchemy_to_json_schema.walkers import (
    ForeignKeyWalker,
    ModelWalker,
    NoForeignKeyWalker,
    StructuralWalker,
)

Base = declarative_base()


class IdMixin:
    _id = Column("id", Integer, primary_key=True)

    @hybrid_property
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, id_: int) -> None:
        self._id = id_


class MyModelWithMixin(Base, IdMixin):
    __tablename__ = "my_model_with_mixin"


class MyModel(Base):
    __tablename__ = "my_model"

    _id = Column("id", Integer, primary_key=True)

    @hybrid_property
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, id_: int) -> None:
        self._id = id_


class MyOtherModel(Base):
    """model for test"""

    __tablename__ = "Group"

    id = Column(Integer, primary_key=True)


class MyModelWithRelationship(Base):
    __tablename__ = "my_model_with_relationship"

    id = Column(Integer, primary_key=True)
    other_model = relationship(MyOtherModel, uselist=False, backref="users")

    _other_model_id = Column(Integer, ForeignKey(MyOtherModel.id), nullable=False)

    @hybrid_property
    def other_model_id(self) -> int:
        return self._other_model_id

    @other_model_id.setter
    def other_model_id(self, other_model_id: int) -> None:
        self._other_model_id = other_model_id


@pytest.mark.parametrize("walker", [ForeignKeyWalker, NoForeignKeyWalker, StructuralWalker])
@pytest.mark.parametrize(
    "model, expected_title",
    [
        pytest.param(MyModel, "MyModel"),
        pytest.param(MyModelWithMixin, "MyModelWithMixin"),
    ],
)
def test_hybrid_property(walker: ModelWalker, model: Type[Base], expected_title: str) -> None:
    schema_factory = SchemaFactory(walker, DefaultClassfier)

    actual = schema_factory(model)

    assert actual == {
        "properties": OrderedDict({"id": {"type": "integer"}}),
        "required": ["id"],
        "title": expected_title,
        "type": "object",
    }


@pytest.mark.parametrize(
    "walker, expected",
    [
        pytest.param(
            NoForeignKeyWalker,
            {
                "properties": OrderedDict({"id": {"type": "integer"}}),
                "required": ["id"],
                "title": "MyModelWithRelationship",
                "type": "object",
            },
        ),
        pytest.param(
            ForeignKeyWalker,
            # Note: `_other_model_id` is returned instead of `other_model_id` because the
            #       `local_table.columns` iterator is returning the real column and not the hybrid
            #       property.
            {
                "properties": OrderedDict(
                    {
                        "id": {"type": "integer"},
                        "_other_model_id": {"type": "integer"},
                    }
                ),
                "required": sorted(["id", "_other_model_id"]),
                "title": "MyModelWithRelationship",
                "type": "object",
            },
        ),
        pytest.param(
            StructuralWalker,
            {
                "definitions": {
                    "MyOtherModel": {
                        "properties": OrderedDict({"id": {"type": "integer"}}),
                        "required": ["id"],
                        "type": "object",
                    },
                },
                "properties": OrderedDict(
                    {
                        "id": {"type": "integer"},
                        "other_model": {"$ref": "#/definitions/MyOtherModel"},
                    },
                ),
                "required": ["id"],
                "title": "MyModelWithRelationship",
                "type": "object",
            },
        ),
    ],
)
@pytest.mark.parametrize("model", [MyModelWithRelationship])
def test_hybrid_property_with_relationship(
    walker: ModelWalker, model: Type[Base], expected: Dict[str, Any]
) -> None:
    schema_factory = SchemaFactory(walker, DefaultClassfier)

    actual = schema_factory(model)

    assert actual == expected
