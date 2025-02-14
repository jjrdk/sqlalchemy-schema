from enum import Enum, unique


@unique
class ColumnPropertyType(Enum):
    RELATIONSHIP = "relationship"
    FOREIGNKEY = "foreignkey"


@unique
class Layout(Enum):
    SWAGGER_2 = "swagger2.0"
    JSON_SCHEMA = "jsonschema"
    OPENAPI_3 = "openapi3.0"
    OPENAPI_2 = "openapi2.0"
    ASYNCAPI_2 = "asyncapi2.0"


@unique
class Format(Enum):
    JSON = "json"
    YAML = "yaml"


@unique
class Walker(Enum):
    STRUCTURAL = "structural"
    NOFOREIGNKEY = "noforeignkey"
    FOREIGNKEY = "foreignkey"


@unique
class Decision(Enum):
    DEFAULT = "default"
    USE_FOREIGN_KEY = "useforeignkey"
