import inspect
from abc import ABC, abstractmethod
from types import ModuleType
from typing import Iterable, Iterator, Optional, Type, Union

from loguru import logger
from sqlalchemy.ext.declarative import DeclarativeMeta
from typing_extensions import TypeGuard

from sqlalchemy_to_json_schema.schema_factory import Schema, SchemaFactory


class AbstractTransformer(ABC):
    def __init__(self, schema_factory: SchemaFactory, /):
        self.schema_factory = schema_factory

    @abstractmethod
    def transform(
        self, rawtargets: Iterable[Union[ModuleType, DeclarativeMeta]], depth: Optional[int], /
    ) -> Schema:
        ...


class JSONSchemaTransformer(AbstractTransformer):
    def transform(
        self, rawtargets: Iterable[Union[ModuleType, DeclarativeMeta]], depth: Optional[int], /
    ) -> Schema:
        definitions = {}

        for item in rawtargets:
            if inspect.isclass(item) and isinstance(item, DeclarativeMeta):
                partial_definitions = self.transform_by_model(item, depth)
            elif inspect.ismodule(item):
                partial_definitions = self.transform_by_module(item, depth)
            else:
                TypeError(f"Expected a class or module, got {item}")

            definitions.update(partial_definitions)

        return definitions

    def transform_by_model(self, model: DeclarativeMeta, depth: Optional[int], /) -> Schema:
        return self.schema_factory(model, depth=depth)

    def transform_by_module(self, module: ModuleType, depth: Optional[int], /) -> Schema:
        subdefinitions = {}
        definitions = {}
        for basemodel in collect_models(module):
            schema = self.schema_factory(basemodel, depth=depth)
            if "definitions" in schema:
                subdefinitions.update(schema.pop("definitions"))
            definitions[schema["title"]] = schema
        d = {}
        d.update(subdefinitions)
        d.update(definitions)
        return {"definitions": definitions}


class OpenAPI2Transformer(AbstractTransformer):
    def transform(
        self, rawtargets: Iterable[Union[ModuleType, DeclarativeMeta]], depth: Optional[int], /
    ) -> Schema:
        definitions = {}

        for target in rawtargets:
            if inspect.isclass(target) and isinstance(target, DeclarativeMeta):
                partial_definitions = self.transform_by_model(target, depth)
            elif inspect.ismodule(target):
                partial_definitions = self.transform_by_module(target, depth)
            else:
                raise TypeError(f"Expected a class or module, got {target}")

            definitions.update(partial_definitions)

        return {"definitions": definitions}

    def transform_by_model(self, model: DeclarativeMeta, depth: Optional[int], /) -> Schema:
        definitions = {}
        schema = self.schema_factory(model, depth=depth)

        if "definitions" in schema:
            definitions.update(schema.pop("definitions"))

        definitions[schema["title"]] = schema

        return definitions

    def transform_by_module(self, module: ModuleType, depth: Optional[int], /) -> Schema:
        subdefinitions = {}
        definitions = {}

        for basemodel in collect_models(module):
            schema = self.schema_factory(basemodel, depth=depth)

            if "definitions" in schema:
                subdefinitions.update(schema.pop("definitions"))

            definitions[schema["title"]] = schema

        d = {}
        d.update(subdefinitions)
        d.update(definitions)

        return definitions


class OpenAPI3Transformer(AbstractTransformer):
    def __init__(self, schema_factory: SchemaFactory, /):
        super().__init__(schema_factory)

        self.oas2transformer = OpenAPI2Transformer(schema_factory)

    def replace_ref(self, d: Union[dict, list], old_prefix: str, new_prefix: str, /) -> None:
        if isinstance(d, dict):
            for k, v in d.items():
                if k == "$ref":
                    d[k] = v.replace(old_prefix, new_prefix)
                else:
                    self.replace_ref(v, old_prefix, new_prefix)
        elif isinstance(d, list):
            for item in d:
                self.replace_ref(item, old_prefix, new_prefix)

    def transform(
        self, rawtargets: Iterable[Union[ModuleType, DeclarativeMeta]], depth: Optional[int], /
    ) -> Schema:
        d = self.oas2transformer.transform(rawtargets, depth)

        self.replace_ref(d, "#/definitions/", "#/components/schemas/")

        if "components" not in d:
            d["components"] = {}
        if "schemas" not in d["components"]:
            d["components"]["schemas"] = {}
        d["components"]["schemas"] = d.pop("definitions", {})
        return d


def collect_models(module: ModuleType, /) -> Iterator[DeclarativeMeta]:
    def is_alchemy_model(maybe_model: Type, /) -> TypeGuard[DeclarativeMeta]:
        if not inspect.isclass(maybe_model):
            return False

        if not (hasattr(maybe_model, "__table__") or hasattr(maybe_model, "__tablename__")):
            return False

        logger.debug("{maybe_model} is a SQLAlchemy model", maybe_model=maybe_model)

        return True

    items: Iterable[Type]

    if hasattr(module, "__all__"):
        logger.debug("Module {module} has an __all__ attribute", module=module)

        items = (getattr(module, name) for name in module.__all__)
    else:
        items = module.__dict__.values()

    models = (item for item in items if is_alchemy_model(item))

    return models


class AsyncAPI2Transformer(OpenAPI3Transformer):
    pass
