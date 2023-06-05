import sqlalchemy as sa
import sqlalchemy.orm as orm

from tests.fixtures.models.base import Base


class Group(Base):
    __tablename__ = "Group"

    pk = sa.Column(sa.Integer, primary_key=True, doc="primary key")
    name = sa.Column(sa.String(255), default="", nullable=False)
    color = sa.Column(sa.Enum("red", "green", "yellow", "blue"))
    created_at = sa.Column(sa.DateTime, nullable=True)


class User(Base):
    __tablename__ = "User"

    pk = sa.Column(sa.Integer, primary_key=True, doc="primary key")
    name = sa.Column(sa.String(255), default="", nullable=False)
    group_id = sa.Column(sa.Integer, sa.ForeignKey(Group.pk), nullable=False)
    address_id = sa.Column(sa.Integer, sa.ForeignKey("Address.pk"), nullable=False)
    group = orm.relationship(Group, uselist=False, backref="users")
    address = orm.relationship("Address", uselist=False, backref="users")
    created_at = sa.Column(sa.DateTime, nullable=True)
