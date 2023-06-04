from importlib import import_module


def load_module_or_symbol(module_path: str) -> object:
    module_path_split = module_path.split(":", maxsplit=1)

    if len(module_path_split) == 1:
        module = import_module(module_path_split[0])

        return module

    else:
        module_name, symbol_name = module_path_split

        module = import_module(module_name)
        symbol = getattr(module, symbol_name)

        return symbol
