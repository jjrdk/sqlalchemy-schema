from datetime import datetime
from typing import Any, Callable, Optional, Type, Union

import pytest
import sqlalchemy as sa
from sqlalchemy import FetchedValue, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.elements import TextClause
from sqlalchemy.sql.expression import ColumnElement

from sqlalchemy_to_json_schema import SchemaFactory
from sqlalchemy_to_json_schema.walkers import (
    ForeignKeyWalker,
    ModelWalker,
    NoForeignKeyWalker,
    StructuralWalker,
)

Base = declarative_base()


def _makeOne(walker: Type[ModelWalker], /) -> SchemaFactory:
    return SchemaFactory(walker)


@pytest.mark.parametrize("walker_cls", [ForeignKeyWalker, NoForeignKeyWalker, StructuralWalker])
@pytest.mark.parametrize("server_default", [None, func.sysdate()])
@pytest.mark.parametrize("default", [None, datetime.now])
def test_detect__nullable_is_True__not_required(
    walker_cls: Type[ModelWalker],
    default: Optional[Callable[..., datetime]],
    server_default: Optional[Union[FetchedValue, str, TextClause, ColumnElement[Any], None]],
) -> None:
    class Model(Base):
        __tablename__ = f"model_nullable_true_{walker_cls}_{default}_{server_default}"

        pk = sa.Column(sa.Integer, primary_key=True, doc="primary key")
        created_at = sa.Column(
            sa.DateTime, nullable=True, default=default, server_default=server_default
        )

    target = _makeOne(walker_cls)
    walker = target.walker(Model)

    result = target._detect_required(walker)

    assert result == ["pk"]


@pytest.mark.parametrize("server_default", [None, func.sysdate()])
@pytest.mark.parametrize("default", [None, datetime.now])
@pytest.mark.parametrize("walker_cls", [ForeignKeyWalker, NoForeignKeyWalker, StructuralWalker])
def test_detect__nullable_is_False__required(
    walker_cls: Type[ModelWalker],
    default: Optional[Callable[..., datetime]],
    server_default: Optional[Callable[..., datetime]],
) -> None:
    class Model(Base):
        __tablename__ = f"model_nullable_false_{walker_cls}_{default}_{server_default}"

        pk = sa.Column(sa.Integer, primary_key=True, doc="primary key")
        created_at = sa.Column(sa.DateTime, nullable=False, default=default, server_default=None)

    target = _makeOne(walker_cls)
    walker = target.walker(Model)

    result = target._detect_required(walker)

    expected = sorted(["pk", "created_at"])

    assert result == expected


@pytest.mark.parametrize("walker_cls", [ForeignKeyWalker, NoForeignKeyWalker, StructuralWalker])
def test_detect__adjust_required(walker_cls: Type[ModelWalker]) -> None:
    class Model(Base):
        __tablename__ = f"model_adjust_required_{walker_cls}"

        pk = sa.Column(sa.Integer, primary_key=True, doc="primary key")

    target = _makeOne(walker_cls)
    walker = target.walker(Model)

    result = target._detect_required(
        walker,
        adjust_required=lambda prop, default: False if prop.key == "pk" else default,
    )

    assert result == []
