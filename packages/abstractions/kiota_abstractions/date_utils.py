from sys import version_info as sys_version_info
import re
from datetime import datetime, time, timedelta

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


_TIMEDELTA_PATTERN = re.compile(r"^(?P<hours>\d+):(?P<minutes>\d+)(?::(?P<seconds>\d+))?$")


def parse_timedelta_string(text: str) -> timedelta:
    """Checks if a given string is a valid ISO8601 duration string. Or hh:mm:ss format."""
    try:
        return parse_timedelta_from_iso_format(text)
    except ValueError as exc:
        # The previous library also supported hh:mm:ss format
        m = _TIMEDELTA_PATTERN.match(text)
        if not m:
            raise ValueError(f"Invalid timedelta string: {text}") from exc

        hours = int(m.group("hours"))
        minutes = int(m.group("minutes"))
        seconds = int(m.group("seconds") or 0)
        return timedelta(hours=hours, minutes=minutes, seconds=seconds)


_TIME_REPLACEMENT_PATTERN = re.compile(r'(\d)([.,])(\d+)')


def datetime_from_iso_format_compat(text: str) -> datetime:
    """Parses a ISO8601 formatted string into a datetime object."""
    try:
        # Try regular first (faster for most cases)
        return datetime.fromisoformat(text)
    except ValueError as exc:
        # Python 3.10 and below only support fractions of seconds in either 3 or 6 digits
        # Python 3.11+ supports any number of digits

        if sys_version_info[:3] < (3, 11):
            # The following code is a workaround for Python 3.10 and below
            fixed_time = re.sub(
                _TIME_REPLACEMENT_PATTERN,
                lambda x: x.group(1) + "." + x.group(3).ljust(6, '0')[:6], text
            ).replace("Z", "+00:00")
            return datetime.fromisoformat(fixed_time)

        raise exc


def time_from_iso_format_compat(text: str) -> time:
    """Parses a ISO8601 formatted string into a time object."""
    try:
        # Try regular first (faster for most cases)
        return time.fromisoformat(text)
    except ValueError as exc:
        # Python 3.10 and below only support fractions of seconds in either 3 or 6 digits
        # Python 3.11+ supports any number of digits

        if sys_version_info[:3] < (3, 11):
            # The following code is a workaround for Python 3.10 and below
            fixed_time = re.sub(
                _TIME_REPLACEMENT_PATTERN,
                lambda x: x.group(1) + "." + x.group(3).ljust(6, '0')[:6], text
            ).replace("Z", "+00:00")
            return time.fromisoformat(fixed_time)

        raise exc
