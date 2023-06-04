import json
from pathlib import Path
from typing import Any, Dict, NoReturn, Optional

import yaml

from sqlalchemy_to_json_schema import SchemaFactory
from sqlalchemy_to_json_schema.command.transformer import (
    JSONSchemaTransformer,
    OpenAPI2Transformer,
    OpenAPI3Transformer,
)
from sqlalchemy_to_json_schema.decisions import (
    Decision,
    RelationDecision,
    UseForeignKeyIfPossibleDecision,
)
from sqlalchemy_to_json_schema.types import (
    DecisionChoice,
    FormatChoice,
    LayoutChoice,
    WalkerChoice,
)
from sqlalchemy_to_json_schema.utils.imports import load_module_or_symbol
from sqlalchemy_to_json_schema.walkers import (
    ForeignKeyWalker,
    ModelWalker,
    NoForeignKeyWalker,
    StructuralWalker,
)


def detect_walker_factory(walker: WalkerChoice) -> ModelWalker:
    if walker == WalkerChoice.STRUCTURAL:
        return StructuralWalker
    elif walker == WalkerChoice.NOFOREIGNKEY:
        return NoForeignKeyWalker
    elif walker == WalkerChoice.FOREIGNKEY:
        return ForeignKeyWalker

    raise ValueError(walker)


def detect_decision(decision: DecisionChoice) -> Decision:
    if decision == DecisionChoice.DEFAULT:
        return RelationDecision()
    elif decision == DecisionChoice.USE_FOREIGN_KEY:
        return UseForeignKeyIfPossibleDecision()

    raise ValueError(decision)


def detect_transformer(layout: LayoutChoice):
    if layout in [LayoutChoice.SWAGGER_2, LayoutChoice.OPENAPI_2]:
        return OpenAPI2Transformer
    elif layout == LayoutChoice.OPENAPI_3:
        return OpenAPI3Transformer
    elif layout == LayoutChoice.JSON_SCHEMA:
        return JSONSchemaTransformer

    raise ValueError(layout)


class Driver:
    def __init__(self, walker: ModelWalker, decision: DecisionChoice, layout: LayoutChoice):
        self.transformer = self.build_transformer(walker, decision, layout)

    def build_transformer(
        self, walker: ModelWalker, decision: DecisionChoice, layout: LayoutChoice
    ) -> NoReturn:
        walker_factory = detect_walker_factory(walker)
        relation_decision = detect_decision(decision)
        schema_factory = SchemaFactory(walker_factory, relation_decision=relation_decision)
        transformer_factory = detect_transformer(layout)
        return transformer_factory(schema_factory).transform

    def run(
        self, module_path: str, filename: Path, format: Optional[FormatChoice], depth: int = None
    ) -> None:
        data = load_module_or_symbol(module_path)
        result = self.transformer(data, depth=depth)
        self.dump(result, filename, format=format)

    def dump(self, data: Dict[str, Any], filename: Path, format: Optional[FormatChoice]) -> None:
        with filename.open("w") as f:
            if format == FormatChoice.YAML:
                yaml.dump(data, f)
            else:
                json.dump(data, f)
