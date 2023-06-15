from typing import OrderedDict, Type

import pytest
from sqlalchemy import JSON, Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy_to_json_schema import DefaultClassfier, SchemaFactory
from sqlalchemy_to_json_schema.walkers import (
    AbstractWalker,
    ForeignKeyWalker,
    NoForeignKeyWalker,
    StructuralWalker,
)

Base = declarative_base()


class MyModel(Base):
    __tablename__ = "my_model"

    id = Column(UUID, primary_key=True)
    data = Column(JSON)


@pytest.mark.parametrize("walker", [ForeignKeyWalker, NoForeignKeyWalker, StructuralWalker])
def test_json(walker: Type[AbstractWalker]) -> None:
    schema_factory = SchemaFactory(walker, DefaultClassfier)

    actual = schema_factory(MyModel)

    assert actual == {
        "properties": OrderedDict(
            {
                "id": {"type": "string", "format": "uuid"},
                "data": {"type": "object"},
            }
        ),
        "required": ["id"],
        "title": "MyModel",
        "type": "object",
    }
