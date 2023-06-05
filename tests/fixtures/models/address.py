import sqlalchemy as sa

from tests.fixtures.models.base import Base


class Address(Base):
    __tablename__ = "Address"

    pk = sa.Column(sa.Integer, primary_key=True, doc="primary key")
    street = sa.Column(sa.String(255), nullable=False)
    town = sa.Column(sa.String(255), nullable=False)
