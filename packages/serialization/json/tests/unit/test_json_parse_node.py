import json
from datetime import date, datetime, time, timedelta, timezone
from uuid import UUID

import pytest
from kiota_serialization_json.json_parse_node import JsonParseNode
from ..helpers import OfficeLocation, User


def test_get_str_value():
    parse_node = JsonParseNode("Diego Siciliani")
    result = parse_node.get_str_value()
    assert result == "Diego Siciliani"


def test_get_int_value():
    parse_node = JsonParseNode(1454)
    result = parse_node.get_int_value()
    assert result == 1454


def test_get_bool_value():
    parse_node = JsonParseNode(False)
    result = parse_node.get_bool_value()
    assert result is False


def test_get_float_value_from_float():
    """
    This test is to ensure that the get_float_value method returns a float when the value is a float
    """
    parse_node = JsonParseNode(44.6)
    result = parse_node.get_float_value()
    assert isinstance(result, float)
    assert result == 44.6


@pytest.mark.parametrize("value", [0, 10, 100])
def test_get_float_value(value: int):
    """
    Consider an OpenAPI Specification using the type: number and format: float or double
    Note: The OpenAPI Specification also allows for the use of the type: integer and format: int32 or int64

    Consider an API with Price data [0, 0.5, 1, 1.5, 2] and so on
    In this case, the contract must define the type as a number, with a hint of float or double as the format

    Kiota should be able to parse the response as a float, even if the value is an integer, because it's still a number.
    """
    parse_node = JsonParseNode(value)
    result = parse_node.get_float_value()
    assert isinstance(result, float)
    assert result == float(value)


def test_get_uuid_value():
    parse_node = JsonParseNode("f58411c7-ae78-4d3c-bb0d-3f24d948de41")
    result = parse_node.get_uuid_value()
    assert result == UUID("f58411c7-ae78-4d3c-bb0d-3f24d948de41")


@pytest.mark.parametrize("value", ["", " ", "  ", "2022-01-0"])
def test_get_datetime_value_returns_none_with_invalid_str(value: str):
    parse_node = JsonParseNode(value)
    result = parse_node.get_datetime_value()
    assert result is None


def test_get_datetime_value():
    parse_node = JsonParseNode("2022-01-27T12:59:45.596117")
    result = parse_node.get_datetime_value()
    assert isinstance(result, datetime)


def test_get_date_value():
    parse_node = JsonParseNode("2015-04-20")
    result = parse_node.get_date_value()
    assert isinstance(result, date)
    assert str(result) == "2015-04-20"


def test_get_time_value():
    parse_node = JsonParseNode("12:59:45.596117")
    result = parse_node.get_time_value()
    assert isinstance(result, time)
    assert str(result) == "12:59:45.596117"


def test_get_timedelta_value():
    parse_node = JsonParseNode("PT30S")
    result = parse_node.get_timedelta_value()
    assert isinstance(result, timedelta)
    assert str(result) == "0:00:30"


def test_get_collection_of_primitive_values():
    parse_node = JsonParseNode([12.1, 12.2, 12.3, 12.4, 12.5])
    result = parse_node.get_collection_of_primitive_values(float)
    assert result == [12.1, 12.2, 12.3, 12.4, 12.5]


def test_get_collection_of_primitive_values_no_type():
    parse_node = JsonParseNode(["One", "Two", "Three", "Four", "Five"])
    result = parse_node.get_collection_of_primitive_values(None)
    assert result == ["One", "Two", "Three", "Four", "Five"]


def test_get_bytes_value():
    parse_node = JsonParseNode("U2Ftd2VsIGlzIHRoZSBiZXN0")
    result = parse_node.get_bytes_value()
    assert isinstance(result, bytes)
    assert result.decode("utf-8") == "U2Ftd2VsIGlzIHRoZSBiZXN0"


def test_get_bytes_json_compatible():
    parse_node = JsonParseNode({"test": 1})
    result = parse_node.get_bytes_value()
    assert json.loads(result.decode("utf-8")) == {"test": 1}


def test_get_collection_of_enum_values():
    parse_node = JsonParseNode(["dunhill", "oval"])
    result = parse_node.get_collection_of_enum_values(OfficeLocation)
    assert isinstance(result, list)
    assert result == [OfficeLocation.Dunhill, OfficeLocation.Oval]


def test_get_enum_value():
    parse_node = JsonParseNode("dunhill")
    result = parse_node.get_enum_value(OfficeLocation)
    assert isinstance(result, OfficeLocation)
    assert result == OfficeLocation.Dunhill


def test_get_enum_value_for_key_not_found():
    parse_node = JsonParseNode("whitehouse")
    result = parse_node.get_enum_value(OfficeLocation)
    assert result is None


def test_get_anythin_does_not_convert_numeric_chars_to_datetime():
    parse_node = JsonParseNode("1212")
    result = parse_node.try_get_anything("1212")
    assert isinstance(result, str)
    assert result == "1212"


def test_get_anythin_does_not_convert_any_length_numeric_chars_to_datetime():
    parse_node = JsonParseNode("1212")
    result1 = parse_node.try_get_anything("1212")
    parse_node_two = JsonParseNode("-PT15M")
    result2 = parse_node_two.try_get_anything("-PT15M")
    parse_node_three = JsonParseNode("20081008")
    result3 = parse_node_three.try_get_anything("20081008")
    parse_node_four = JsonParseNode("1011317")
    result4 = parse_node_four.try_get_anything("1011317")
    assert isinstance(result1, str)
    assert result1 == "1212"
    assert isinstance(result2, str)
    assert result2 == "-PT15M"
    assert isinstance(result3, str)
    assert result3 == "20081008"
    assert isinstance(result4, str)
    assert result4 == "1011317"


def test_get_anythin_does_convert_date_string_to_datetime():
    parse_node = JsonParseNode("2023-10-05T14:48:00.000Z")
    result = parse_node.try_get_anything("2023-10-05T14:48:00.000Z")
    assert isinstance(result, datetime)
    # there is an issue with parsing the original iso string (Z not supported < 3.11)
    assert result == datetime(2023, 10, 5, 14, 48, tzinfo=timezone.utc)


def test_get_object_value(user1_json):
    parse_node = JsonParseNode(json.loads(user1_json))
    result = parse_node.get_object_value(User)
    assert isinstance(result, User)
    assert result.id == UUID("8f841f30-e6e3-439a-a812-ebd369559c36")
    assert result.office_location == OfficeLocation.Dunhill
    assert isinstance(result.updated_at, datetime)
    assert isinstance(result.birthday, date)
    assert result.business_phones == ["+1 205 555 0108"]
    assert result.is_active is True
    assert result.mobile_phone is None
    assert (
        result.additional_data["additional_data"]["@odata.context"] ==
        "https://graph.microsoft.com/v1.0/$metadata#users/$entity"
    )
    assert result.additional_data["additional_data"]["manager"] == {
        "id": UUID("8f841f30-e6e3-439a-a812-ebd369559c36"),
        "updated_at": datetime(2022, 1, 27, 12, 59, 45, 596117, timezone.utc),
        "is_active": True,
    }
    assert result.additional_data["additional_data"]["approvers"] == [
        {
            "id":
            UUID("8f841f30-e6e3-439a-a812-ebd369559c36"),
            "updated_at": datetime(2022, 1, 27, 12, 59, 45, 596117, timezone.utc),
            "is_active":
            True,
        },
        {
            "display_name": "John Doe",
            "age": 32
        },
    ]
    assert result.additional_data["additional_data"]["data"] == {
        "groups": [{
            "friends": [{
                "display_name": "John Doe",
                "age": 32
            }]
        }]
    }


def test_get_collection_of_object_values(users_json):
    parse_node = JsonParseNode(json.loads(users_json))
    result = parse_node.get_collection_of_object_values(User)
    assert isinstance(result[0], User)
    assert result[0].id == UUID("8f841f30-e6e3-439a-a812-ebd369559c36")
    assert result[0].office_location == OfficeLocation.Dunhill
    assert isinstance(result[0].updated_at, datetime)
    assert isinstance(result[0].birthday, date)
    assert result[0].business_phones == ["+1 205 555 0108"]
    assert result[0].is_active is True
    assert result[0].mobile_phone is None
