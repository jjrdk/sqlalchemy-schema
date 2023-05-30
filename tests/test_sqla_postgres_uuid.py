from typing import OrderedDict

import pytest
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy_to_json_schema import (
    DefaultClassfier,
    ForeignKeyWalker,
    ModelWalker,
    NoForeignKeyWalker,
    SchemaFactory,
    StructuralWalker,
)

Base = declarative_base()


class MyModel(Base):
    __tablename__ = "my_model"

    id = Column("id", UUID, primary_key=True)


@pytest.mark.parametrize("walker", [ForeignKeyWalker, NoForeignKeyWalker, StructuralWalker])
def test_hybrid_property(walker: ModelWalker) -> None:
    schema_factory = SchemaFactory(walker, DefaultClassfier)

    actual = schema_factory(MyModel)

    assert actual == {
        "properties": OrderedDict({"id": {"type": "string", "format": "uuid"}}),
        "required": ["id"],
        "title": "MyModel",
        "type": "object",
    }
