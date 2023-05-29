class ErrorFound(Exception):  # xxx:
    def __init__(self, errors):
        self.errors = errors


class InvalidStatus(Exception):
    pass


class ConversionError(Exception):
    def __init__(self, name, message):
        self.name = name
        self.message = message
