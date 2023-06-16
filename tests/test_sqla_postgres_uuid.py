from typing import Type

import pytest
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy_to_json_schema.schema_factory import SchemaFactory
from sqlalchemy_to_json_schema.walkers import (
    AbstractWalker,
    ForeignKeyWalker,
    NoForeignKeyWalker,
    StructuralWalker,
)

Base = declarative_base()


class MyModel(Base):
    __tablename__ = "my_model"

    id = Column("id", UUID, primary_key=True)


@pytest.mark.parametrize("walker", [ForeignKeyWalker, NoForeignKeyWalker, StructuralWalker])
def test_hybrid_property(walker: Type[AbstractWalker]) -> None:
    schema_factory = SchemaFactory(walker)

    actual = schema_factory(MyModel)

    assert actual == {
        "properties": {"id": {"type": "string", "format": "uuid"}},
        "required": ["id"],
        "title": "MyModel",
        "type": "object",
    }
