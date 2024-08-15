from collections.abc import Sequence


class ErrorFound(Exception):  # xxx:
    def __init__(self, errors: Sequence[str], /):
        self.errors = errors


class InvalidStatus(Exception):
    pass


class ConversionError(Exception):
    def __init__(self, name: str, message: str, /):
        self.name = name
        self.message = message
