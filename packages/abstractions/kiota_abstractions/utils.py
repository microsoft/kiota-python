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


_ISO8601_DURATION_PATTERN = re.compile(
    "^P"  # Duration P indicator
    # Weeks
    "(?P<w>"
    r"    (?P<weeks>\d+(?:[.,]\d+)?W)"
    ")?"
    # Years, Months, Days
    "(?P<ymd>"
    r"    (?P<years>\d+(?:[.,]\d+)?Y)?"
    r"    (?P<months>\d+(?:[.,]\d+)?M)?"
    r"    (?P<days>\d+(?:[.,]\d+)?D)?"
    ")?"
    # Time
    "(?P<hms>"
    "    (?P<timesep>T)"  # Separator (T)
    r"    (?P<hours>\d+(?:[.,]\d+)?H)?"
    r"    (?P<minutes>\d+(?:[.,]\d+)?M)?"
    r"    (?P<seconds>\d+(?:[.,]\d+)?S)?"
    ")?"
    "$",
    re.VERBOSE,
)


def parse_timedelta_from_iso_format(text: str) -> timedelta:
    """Parses a ISO8601 duration string into a timedelta object."""

    m = _ISO8601_DURATION_PATTERN.match(text)
    if not m:
        raise ValueError(f"Invalid ISO8601 duration string: {text}")

    weeks = float(m.group("weeks").replace(",", ".").replace("W", "")) if m.group("weeks") else 0
    years = float(m.group("years").replace(",", ".").replace("Y", "")) if m.group("years") else 0
    months = float(m.group("months").replace(",", ".").replace("M", "")) if m.group("months") else 0
    days = float(m.group("days").replace(",", ".").replace("D", "")) if m.group("days") else 0
    hours = float(m.group("hours").replace(",", ".").replace("H", "")) if m.group("hours") else 0
    minutes = float(m.group("minutes").replace(",", ".").replace("M", "")
                    ) if m.group("minutes") else 0
    seconds = float(m.group("seconds").replace(",", ".").replace("S", "")
                    ) if m.group("seconds") else 0
    _have_date = years or months or days
    _have_time = hours or minutes or seconds
    if weeks and (_have_date or _have_time):
        raise ValueError("Combining weeks with other date/time parts is not supported")

    _total_days = (years * 365) + (months * 30) + days
    return timedelta(
        days=_total_days,
        hours=hours,
        minutes=minutes,
        seconds=seconds,
        weeks=weeks,
    )
