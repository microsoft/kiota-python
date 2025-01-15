import pytest

from kiota_abstractions.utils import parse_timedelta_from_iso_format


def test_parse_timedelta_from_iso_format_weeks():
    result = parse_timedelta_from_iso_format("P3W")
    assert result.days == 21


def test_parse_timedelta_from_iso_format_days():
    result = parse_timedelta_from_iso_format("P3D")
    assert result.days == 3


def test_parse_timedelta_from_iso_format_hours():
    result = parse_timedelta_from_iso_format("PT3H")
    assert result.seconds == 10800


def test_parse_timedelta_from_iso_format_minutes():
    result = parse_timedelta_from_iso_format("PT3M")
    assert result.seconds == 180


def test_parse_timedelta_from_iso_format_seconds():
    result = parse_timedelta_from_iso_format("PT3S")
    assert result.seconds == 3


def test_parse_timedelta_from_iso_format_years():
    result = parse_timedelta_from_iso_format("P3Y")
    assert result.days == 1095


def test_parse_timedelta_from_iso_format_months():
    result = parse_timedelta_from_iso_format("P3M")
    assert result.days == 90


def test_parse_timedelta_from_iso_format_days_and_time():
    result = parse_timedelta_from_iso_format("P3DT3H3M3S")
    assert result.days == 3
    assert result.seconds == 10983


def test_parse_timedelta_from_iso_format_weeks_and_years():
    # assert this raises a ValueError
    with pytest.raises(ValueError):
        parse_timedelta_from_iso_format("P3W3Y")


def test_parse_timedelta_from_iso_format_years_and_weeks():
    # assert this raises a ValueError
    with pytest.raises(ValueError):
        parse_timedelta_from_iso_format("P3Y3W")
