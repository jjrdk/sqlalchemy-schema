from datetime import datetime
from typing import Any, Callable, Optional, Type, Union

import pytest
import sqlalchemy as sa
from sqlalchemy import FetchedValue, func
from sqlalchemy.sql.elements import TextClause
from sqlalchemy.sql.expression import ColumnElement

from sqlalchemy_to_json_schema.schema_factory import SchemaFactory
from sqlalchemy_to_json_schema.walkers import (
    AbstractWalker,
    ForeignKeyWalker,
    NoForeignKeyWalker,
    StructuralWalker,
)
from tests.fixtures.models.base import Base


class TestSchemaFactory:
    @pytest.mark.parametrize(
        "walker_cls", [ForeignKeyWalker, NoForeignKeyWalker, StructuralWalker]
    )
    @pytest.mark.parametrize("server_default", [None, func.sysdate()])
    @pytest.mark.parametrize("default", [None, datetime.now])
    def test_detect__nullable_is_True__not_required(
        self,
        walker_cls: Type[AbstractWalker],
        default: Optional[Callable[..., datetime]],
        server_default: Optional[Union[FetchedValue, str, TextClause, ColumnElement[Any], None]],
    ) -> None:
        class Model(Base):
            __tablename__ = f"model_nullable_true_{walker_cls}_{default}_{server_default}"

            pk = sa.Column(sa.Integer, primary_key=True, doc="primary key")
            created_at = sa.Column(
                sa.DateTime, nullable=True, default=default, server_default=server_default
            )

        target = SchemaFactory(walker_cls)
        walker = target.walker(Model)

        result = target._detect_required(walker)

        assert result == ["pk"]

    @pytest.mark.parametrize("server_default", [None, func.sysdate()])
    @pytest.mark.parametrize("default", [None, datetime.now])
    @pytest.mark.parametrize(
        "walker_cls", [ForeignKeyWalker, NoForeignKeyWalker, StructuralWalker]
    )
    def test_detect__nullable_is_False__required(
        self,
        walker_cls: Type[AbstractWalker],
        default: Optional[Callable[..., datetime]],
        server_default: Optional[Callable[..., datetime]],
    ) -> None:
        class Model(Base):
            __tablename__ = f"model_nullable_false_{walker_cls}_{default}_{server_default}"

            pk = sa.Column(sa.Integer, primary_key=True, doc="primary key")
            created_at = sa.Column(
                sa.DateTime, nullable=False, default=default, server_default=None
            )

        target = SchemaFactory(walker_cls)
        walker = target.walker(Model)

        result = target._detect_required(walker)

        expected = sorted(["pk", "created_at"])

        assert result == expected

    @pytest.mark.parametrize(
        "walker_cls", [ForeignKeyWalker, NoForeignKeyWalker, StructuralWalker]
    )
    def test_detect__adjust_required(self, walker_cls: Type[AbstractWalker]) -> None:
        class Model(Base):
            __tablename__ = f"model_adjust_required_{walker_cls}"

            pk = sa.Column(sa.Integer, primary_key=True, doc="primary key")

        target = SchemaFactory(walker_cls)
        walker = target.walker(Model)

        result = target._detect_required(
            walker,
            adjust_required=lambda prop, default: False if prop.key == "pk" else default,
        )

        assert result == []
