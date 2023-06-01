from enum import Enum, unique


@unique
class ColumnPropertyType(Enum):
    RELATIONSHIP = "relationship"
    FOREIGNKEY = "foreignkey"


@unique
class LayoutChoice(Enum):
    SWAGGER_2 = "swagger2.0"
    JSON_SCHEMA = "jsonschema"
    OPENAPI_3 = "openapi3.0"
    OPENAPI_2 = "openapi2.0"
