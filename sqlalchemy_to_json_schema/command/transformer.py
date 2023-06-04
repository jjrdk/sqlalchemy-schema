import inspect
from abc import ABC, abstractmethod
from types import ModuleType

from dictknife import DictWalker

from sqlalchemy_to_json_schema import Schema, SchemaFactory


class Transformer(ABC):
    def __init__(self, schema_factory: SchemaFactory):
        self.schema_factory = schema_factory

    @abstractmethod
    def transform(self, rawtarget: ModuleType, depth: int) -> Schema:
        ...


class JSONSchemaTransformer(Transformer):
    def transform(self, rawtarget: ModuleType, depth: int) -> Schema:
        if not inspect.isclass(rawtarget):
            raise RuntimeError("please passing the path of model class (e.g. foo.boo:Model)")
        return self.schema_factory(rawtarget, depth=depth)


class OpenAPI2Transformer(Transformer):
    def transform(self, rawtarget: ModuleType, depth: int) -> Schema:
        if inspect.isclass(rawtarget):
            return self.transform_by_model(rawtarget, depth)
        else:
            return self.transform_by_module(rawtarget, depth)

    def transform_by_model(self, model, depth):
        definitions = {}
        schema = self.schema_factory(model, depth=depth)
        if "definitions" in schema:
            definitions.update(schema.pop("definitions"))
        definitions[schema["title"]] = schema
        return {"definitions": definitions}

    def transform_by_module(self, module, depth):
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


class OpenAPI3Transformer(Transformer):
    def __init__(self, schema_factory):
        super().__init__(schema_factory)

        self.oas2transformer = OpenAPI2Transformer(schema_factory)

    def transform(self, rawtarget: ModuleType, depth: int) -> Schema:
        d = self.oas2transformer.transform(rawtarget, depth)
        for _, sd in DictWalker(["$ref"]).walk(d):
            sd["$ref"] = sd["$ref"].replace("#/definitions/", "#/components/schemas/")
        if "components" not in d:
            d["components"] = {}
        if "schemas" not in d["components"]:
            d["components"]["schemas"] = {}
        d["components"]["schemas"] = d.pop("definitions", {})
        return d


def collect_models(module):
    def is_alchemy_model(maybe_model):
        return hasattr(maybe_model, "__table__") or hasattr(maybe_model, "__tablename__")

    if hasattr(module, "__all__"):
        return [getattr(module, name) for name in module.__all__]
    else:
        return [value for name, value in module.__dict__.items() if is_alchemy_model(value)]
