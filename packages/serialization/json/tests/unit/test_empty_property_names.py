import json
from datetime import date, datetime, time, timedelta
from uuid import UUID

import pytest

from kiota_serialization_json.json_serialization_writer import JsonSerializationWriter

from ..helpers import OfficeLocation, User


@pytest.mark.parametrize("key", ["", "named", None])
@pytest.mark.parametrize("method,value,expected", [
    ("write_str_value", "text", "text"),
    ("write_bool_value", True, True),
    ("write_int_value", 42, 42),
    ("write_float_value", 1.5, 1.5),
    ("write_uuid_value", UUID(int=1), str(UUID(int=1))),
    ("write_datetime_value", datetime(2026, 1, 2, 3, 4), "2026-01-02T03:04:00"),
    ("write_date_value", date(2026, 1, 2), "2026-01-02"),
    ("write_time_value", time(3, 4), "03:04:00"),
    ("write_timedelta_value", timedelta(seconds=1), "0:00:01"),
    ("write_bytes_value", b"hello", "aGVsbG8="),
    ("write_collection_of_primitive_values", [1, 2], [1, 2]),
    ("write_enum_value", OfficeLocation.Oval, "oval"),
    ("write_collection_of_enum_values", [OfficeLocation.Oval], ["oval"]),
])
def test_property_name_is_distinct_from_root(key, method, value, expected):
    writer = JsonSerializationWriter()
    getattr(writer, method)(key, value)
    assert json.loads(writer.get_serialized_content()) == (
        expected if key is None else {key: expected}
    )


@pytest.mark.parametrize("value", [None, "", False, 0, {}, {"": {}}, [{"": "value"}]])
def test_nested_additional_data_preserves_empty_names(value):
    writer = JsonSerializationWriter()
    writer.write_additional_data_value({"properties": {"": value}})
    assert json.loads(writer.get_serialized_content()) == {"properties": {"": value}}


@pytest.mark.parametrize("collection", [False, True])
def test_model_with_empty_property_name(collection):
    user = User()
    user.mobile_phone = "123"
    writer = JsonSerializationWriter()
    if collection:
        writer.write_collection_of_object_values("", [user])
    else:
        writer.write_object_value("", user)
    expected = {"mobile_phone": "123"}
    assert json.loads(writer.get_serialized_content()) == {"": [expected] if collection else expected}
