import inspect
from abc import ABC, abstractmethod
from collections import deque
from types import ModuleType

from sqlalchemy_to_json_schema import Schema, SchemaFactory


def apply(q, v, *args):
    if callable(q):
        return q(v, *args)
    else:
        return q == v


class ContainerHandler:
    def identity(self, *args):
        return args

    def __call__(self, walker, ctx, d, k):
        return ctx(walker, self.identity, d)


class PathContext:
    def __init__(self):
        self.path = []

    def push(self, v):
        self.path.append(v)

    def pop(self):
        self.path.pop()

    def __call__(self, walker, fn, value):
        return fn(self.path, value)


class DictWalker:
    context_factory = PathContext
    handler_factory = ContainerHandler

    def __init__(self, qs, handler=None, context_factory=None):
        self.qs = qs
        self.context_factory = context_factory or self.__class__.context_factory
        self.handler = handler or self.__class__.handler_factory()

    def on_found(self, ctx, d, k):
        yield self.handler(self, ctx, d, k)

    def create_context(self, ctx=None):
        return ctx or self.context_factory()

    def walk(self, d, qs=None, depth=-1, ctx=None):
        qs = qs or self.qs
        ctx = self.create_context(ctx)
        return self._walk(ctx, deque(self.qs), d, depth=depth)

    def _walk(self, ctx, qs, d, depth):
        if depth == 0:
            return

        if not qs:
            return

        if hasattr(d, "keys"):
            for k, v in list(d.items()):
                ctx.push(k)
                if apply(qs[0], k, v):
                    q = qs.popleft()
                    yield from self._walk(ctx, qs, d[k], depth - 1)
                    if len(qs) == 0:
                        yield from self.on_found(ctx, d, k)
                    qs.appendleft(q)
                else:
                    yield from self._walk(ctx, qs, d[k], depth)
                ctx.pop()
            return
        elif isinstance(d, (list, tuple)):
            for i, e in enumerate(d):
                ctx.push(i)
                yield from self._walk(ctx, qs, e, depth)
                ctx.pop()
            return
        else:
            return

    iterate = walk  # for backward compatibility


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
