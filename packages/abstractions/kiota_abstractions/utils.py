import importlib.util
import sys
import re
from datetime import timedelta

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

def parseTimeDeltaFromIsoFormat(duration_str):
    """Parses an ISO 8601 duration string into a timedelta object.

    Args:
        duration_str (str): The ISO 8601 duration string.

    Returns:
        timedelta: The parsed timedelta object.
    """
    pattern = re.compile(
        r'P'  # starts with 'P'
        r'(?:(\d+)Y)?'  # years
        r'(?:(\d+)M)?'  # months
        r'(?:(\d+)D)?'  # days
        r'(?:T'  # time part starts with 'T'
        r'(?:(\d+)H)?'  # hours
        r'(?:(\d+)M)?'  # minutes
        r'(?:(\d+)S)?)?'  # seconds
    )
    match = pattern.fullmatch(duration_str)
    if not match:
        raise ValueError(f"Invalid ISO 8601 duration string: {duration_str}")

    years, months, days, hours, minutes, seconds = match.groups()
    return timedelta(
        days=int(days or 0) + int(years or 0) * 365 + int(months or 0) * 30,
        hours=int(hours or 0),
        minutes=int(minutes or 0),
        seconds=int(seconds or 0)
    )
