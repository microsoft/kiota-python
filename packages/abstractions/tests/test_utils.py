import pytest

from kiota_abstractions.utils import parseTimeDeltaFromIsoFormat

def test_parseTimeDeltaFromIsoFormat_weeks():
    result = parseTimeDeltaFromIsoFormat("P3W")
    assert result.days == 21

def test_parseTimeDeltaFromIsoFormat_days():
    result = parseTimeDeltaFromIsoFormat("P3D")
    assert result.days == 3

def test_parseTimeDeltaFromIsoFormat_hours():
    result = parseTimeDeltaFromIsoFormat("PT3H")
    assert result.seconds == 10800

def test_parseTimeDeltaFromIsoFormat_minutes():
    result = parseTimeDeltaFromIsoFormat("PT3M")
    assert result.seconds == 180

def test_parseTimeDeltaFromIsoFormat_seconds():
    result = parseTimeDeltaFromIsoFormat("PT3S")
    assert result.seconds == 3

def test_parseTimeDeltaFromIsoFormat_years():
    result = parseTimeDeltaFromIsoFormat("P3Y")
    assert result.days == 1095

def test_parseTimeDeltaFromIsoFormat_months():
    result = parseTimeDeltaFromIsoFormat("P3M")
    assert result.days == 90

# This is "invalid" according to the ISO 8601 standard, but python also supports it
def test_parseTimeDeltaFromIsoFormat_weeks_and_years():
    result = parseTimeDeltaFromIsoFormat("P3Y3W")
    assert result.days == 1122

def test_parseTimeDeltaFromIsoFormat_days_and_time():
    result = parseTimeDeltaFromIsoFormat("P3DT3H3M3S")
    assert result.days == 3
    assert result.seconds == 10983
