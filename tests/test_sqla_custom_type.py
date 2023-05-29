import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

# definition
from sqlalchemy.types import BigInteger, Integer

from sqlalchemy_to_json_schema import DefaultClassfier, ForeignKeyWalker, SchemaFactory


def _getTarget():
    return SchemaFactory


def _makeOne(*args, **kwargs):
    return _getTarget()(ForeignKeyWalker, DefaultClassfier)


Base = declarative_base()


class Identifier(Integer):
    def __init__(self, inner):
        self.inner = inner

    def _compiler_dispatch(self, visitor, **kw):
        return self.inner._compiler_dispatch(visitor, **kw)

    def is_not_support_big_integer(self):
        return True

    def get_dbapi_type(self, dbapi):
        return self.inner.get_dbapi_type(dbapi)

    @property
    def python_type(self):
        return self.inner.python_type

    @property
    def _expression_adaptations(self):
        return self.inner._expression_adaptations


class MyModel(Base):
    __tablename__ = "MyModel"
    pk = sa.Column(Identifier(BigInteger), primary_key=True)


class MyModel2(Base):
    __tablename__ = "MyModel2"
    pk = sa.Column(Identifier(Integer), primary_key=True)


def test_it():
    target = _makeOne()
    result = target(MyModel)
    assert result["properties"] == {"pk": {"type": "integer"}}


def test_it2():
    target = _makeOne()
    result = target(MyModel)
    assert result["properties"] == {"pk": {"type": "integer"}}
