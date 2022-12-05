import importlib.util
import sys


def lazy_import(name: str):
    """Lazily imports a python module given its absolute path

    Args:
        name (str): Absolute path to the module

    Returns:
        module: The module to be imported
    """
    spec = importlib.util.find_spec(name)

    loader = importlib.util.LazyLoader(spec.loader)

    spec.loader = loader

    module = importlib.util.module_from_spec(spec)

    sys.modules[name] = module

    loader.exec_module(module)

    return module
