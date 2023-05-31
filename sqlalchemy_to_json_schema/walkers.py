from abc import ABC, abstractmethod
from typing import Iterator

from sqlalchemy.inspection import inspect
from sqlalchemy.orm.properties import ColumnProperty
from sqlalchemy.orm.relationships import RelationshipProperty

from sqlalchemy_to_json_schema.exceptions import InvalidStatus


class ModelWalker(ABC):
    def __init__(self, model, includes=None, excludes=None, history=None):
        self.mapper = inspect(model).mapper
        self.includes = includes
        self.excludes = excludes
        self.history = history or []
        if includes and excludes:
            if set(includes).intersection(excludes):
                raise InvalidStatus(f"Conflict includes={includes}, exclude={excludes}")

    def clone(self, name, mapper, includes, excludes, history):
        return self.__class__(mapper, includes, excludes, history)

    def from_child(self, model):
        return self.__class__(model, history=self.history)

    @abstractmethod
    def walk(self) -> Iterator[ColumnProperty]:
        pass


# mapper.column_attrs and mapper.attrs is not ordered. define our custom iterate function `iterate'


class ForeignKeyWalker(ModelWalker):
    def iterate(self) -> Iterator[ColumnProperty]:
        for c in self.mapper.local_table.columns:
            if c.name not in self.mapper._props:
                for prop in self.mapper.iterate_properties:
                    if isinstance(prop, ColumnProperty):
                        columns = {column.name for column in prop.columns}

                        if c.name in columns:
                            yield prop  # danger!! not immutable
            else:
                yield self.mapper._props[c.name]  # danger!! not immutable

    def walk(self):
        for prop in self.iterate():
            if self.includes is None or prop.key in self.includes:
                if self.excludes is None or prop.key not in self.excludes:
                    yield prop


class NoForeignKeyWalker(ModelWalker):
    def iterate(self) -> Iterator[ColumnProperty]:
        for c in self.mapper.local_table.columns:
            if c.name not in self.mapper._props:
                for prop in self.mapper.iterate_properties:
                    if isinstance(prop, ColumnProperty):
                        columns = {column.name for column in prop.columns}

                        if c.name in columns:
                            yield prop  # danger!! not immutable
            else:
                yield self.mapper._props[c.name]  # danger!! not immutable

    def walk(self):
        for prop in self.iterate():
            if self.includes is None or prop.key in self.includes:
                if self.excludes is None or prop.key not in self.excludes:
                    if not any(c.foreign_keys for c in getattr(prop, "columns", {})):
                        yield prop


class StructuralWalker(ModelWalker):
    def iterate(self):
        for c in self.mapper.local_table.columns:
            if c.name not in self.mapper._props:
                for prop in self.mapper.iterate_properties:
                    if isinstance(prop, ColumnProperty):
                        columns = {column.name for column in prop.columns}

                        if c.name in columns:
                            yield prop  # danger!! not immutable
            else:
                yield self.mapper._props[c.name]  # danger!! not immutable
        for prop in self.mapper.relationships:
            yield prop

    def walk(self):
        for prop in self.iterate():
            if isinstance(prop, (ColumnProperty, RelationshipProperty)):
                if self.includes is None or prop.key in self.includes:
                    if self.excludes is None or prop.key not in self.excludes:
                        if prop not in self.history:
                            if not any(c.foreign_keys for c in getattr(prop, "columns", {})):
                                yield prop
