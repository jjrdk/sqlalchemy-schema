import inspect
from abc import ABC, abstractmethod
from types import ModuleType
from typing import Iterable, List, Optional, Type, Union

from sqlalchemy.ext.declarative import DeclarativeMeta

from sqlalchemy_to_json_schema import Schema, SchemaFactory


class Transformer(ABC):
    def __init__(self, schema_factory: SchemaFactory, /):
        self.schema_factory = schema_factory

    @abstractmethod
    def transform(
        self, rawtargets: Iterable[Union[ModuleType, DeclarativeMeta]], depth: Optional[int], /
    ) -> Schema:
        ...


class JSONSchemaTransformer(Transformer):
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


class OpenAPI2Transformer(Transformer):
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


class OpenAPI3Transformer(Transformer):
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


def collect_models(module: ModuleType) -> List[DeclarativeMeta]:
    def is_alchemy_model(maybe_model: Type, /) -> bool:
        return hasattr(maybe_model, "__table__") or hasattr(maybe_model, "__tablename__")

    if hasattr(module, "__all__"):
        return [getattr(module, name) for name in module.__all__]
    else:
        return [value for name, value in module.__dict__.items() if is_alchemy_model(value)]
