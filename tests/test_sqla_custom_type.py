from typing import Any, Type

import sqlalchemy as sa
from sqlalchemy import BigInteger, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.type_api import TypeEngine

from sqlalchemy_to_json_schema import DefaultClassfier, SchemaFactory
from sqlalchemy_to_json_schema.walkers import ForeignKeyWalker

# definition


def _makeOne() -> SchemaFactory:
    return SchemaFactory(ForeignKeyWalker, DefaultClassfier)


Base = declarative_base()


class Identifier(Integer):
    def __init__(self, inner: Type[TypeEngine]) -> None:
        self.inner = inner

    def _compiler_dispatch(self, visitor: Any, **kw: Any) -> Any:
        return self.inner._compiler_dispatch(visitor, **kw)  # type: ignore[attr-defined]

    def is_not_support_big_integer(self) -> bool:
        return True

    def get_dbapi_type(self, dbapi: Any) -> Any:
        return self.inner.get_dbapi_type(dbapi)  # type: ignore[call-arg]

    @property
    def python_type(self) -> Any:
        return self.inner.python_type

    @property
    def _expression_adaptations(self) -> Any:
        return self.inner._expression_adaptations  # type: ignore[attr-defined]


class MyModel(Base):
    __tablename__ = "MyModel"
    pk = sa.Column(Identifier(BigInteger), primary_key=True)


class MyModel2(Base):
    __tablename__ = "MyModel2"
    pk = sa.Column(Identifier(Integer), primary_key=True)


def test_it() -> None:
    target = _makeOne()
    result = target(MyModel)
    assert result["properties"] == {"pk": {"type": "integer"}}


def test_it2() -> None:
    target = _makeOne()
    result = target(MyModel)
    assert result["properties"] == {"pk": {"type": "integer"}}
