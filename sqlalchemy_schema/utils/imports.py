import inspect
from importlib import import_module
from types import ModuleType
from typing import Union

from loguru import logger


def load_module_or_symbol(module_path: str, /) -> Union[ModuleType, type]:
    logger.info("Loading module or symbol from {module_path}", module_path=module_path)

    module_path_split = module_path.split(":", maxsplit=1)

    if len(module_path_split) == 1:
        module = import_module(module_path_split[0])

        return module

    else:
        module_name, symbol_name = module_path_split

        module = import_module(module_name)
        symbol = getattr(module, symbol_name)

        if not inspect.isclass(symbol):
            raise TypeError(f"{symbol} is not a class")

        return symbol
