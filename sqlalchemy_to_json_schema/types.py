from enum import Enum, unique


@unique
class ColumnPropertyType(Enum):
    RELATIONSHIP = "relationship"
    FOREIGNKEY = "foreignkey"
