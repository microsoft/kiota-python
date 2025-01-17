import pytest

from kiota_abstractions.date_utils import (
    parse_timedelta_from_iso_format,
    parse_timedelta_string,
    time_from_iso_format_compat,
    datetime_from_iso_format_compat
)


@pytest.mark.parametrize("text", ["08:00:00", "08:00:00.0", "08:00:00.00","08:00:00.000",
                                  "08:00:00.0000","08:00:00.00000","08:00:00.000000", "08:00:00.0000000", "08:00:00,0000000",
                                  "08:00:00,0000000Z", "08:00:00.00Z", "08:00:00.00+00:00" ])
def test_time_from_iso_format_compat(text: str):
    result = time_from_iso_format_compat(text)
    assert result.hour == 8
    assert result.minute == 0
    assert result.second == 0

@pytest.mark.parametrize("text", ["1986-07-28T08:00:00", "1986-07-28T08:00:00.0", "1986-07-28T08:00:00.00",
                                  "1986-07-28T08:00:00.000", "1986-07-28T08:00:00.0000", "1986-07-28T08:00:00.00000",
                                  "1986-07-28T08:00:00.000000", "1986-07-28T08:00:00.0000000", "1986-07-28T08:00:00,0000000",
                                  "1986-07-28T08:00:00.0000000Z", "1986-07-28T08:00:00.00Z", "1986-07-28T08:00:00.00+00:00" ])
def test_datetime_from_iso_format_compat(text: str):
    result = datetime_from_iso_format_compat(text)
    assert result.hour == 8
    assert result.minute == 0
    assert result.second == 0


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

def test_parse_timedelta_from_iso_format_time_without_p():
    with pytest.raises(ValueError):
        parse_timedelta_from_iso_format("T3H3M3S")

@pytest.mark.parametrize("text", ["P3W3Y", "P3W3Y3D", "P3W3Y3DT3H3M3S"])
def test_parse_timedelta_from_iso_format_must_raise(text: str):
    # assert this raises a ValueError
    with pytest.raises(ValueError):
        parse_timedelta_from_iso_format(text)


@pytest.mark.parametrize("text, expected_hours", [("PT3H", 3), ("2:00:00", 2)])
def test_parse_timedelta_string_valid(text:str, expected_hours:int):
    result = parse_timedelta_string(text)
    assert result.days == 0
    assert result.seconds == expected_hours * 3600
