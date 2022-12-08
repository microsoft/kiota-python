import importlib.util
import sys


def lazy_import(name):
    """Lazily imports a python module given its absolute path.

    Note: This a utility method for use in Kiota generated code only and not
    meant for application outside of that scenario.

    Args:
        name (str): Absolute path to the module

    Returns:
        module: The module to be imported
    """
    if not name or not isinstance(name, str):
        raise ValueError("Module name must be a valid string")

    if name in sys.modules:
        module = sys.modules[name]
        return module

    spec = importlib.util.find_spec(name)

    if not spec:
        raise ValueError(f"No spec found for: {name}")

    loader = importlib.util.LazyLoader(spec.loader)

    spec.loader = loader

    module = importlib.util.module_from_spec(spec)

    sys.modules[name] = module

    loader.exec_module(module)

    return module
