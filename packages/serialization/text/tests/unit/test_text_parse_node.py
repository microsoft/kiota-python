import json
from datetime import date, datetime, time, timedelta
from uuid import UUID

import pytest

from kiota_serialization_text.text_parse_node import TextParseNode

from ..helpers import OfficeLocation, User


@pytest.fixture
def sample_structured_data():
    user_json = json.dumps(
        {
            "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users/$entity",
            "businessPhones": ["+1 425 555 0109"],
            "displayName": "Adele Vance",
            "mobilePhone": None,
            "officeLocation": "dunhill",
            "updatedAt": "2017 -07-29T03:07:25Z",
            "birthday": "2000-09-04",
            "isActive": True,
            "age": 21,
            "gpa": 3.7,
            "id": "76cabd60-f9aa-4d23-8958-64f5539b826a"
        }
    )
    return str(user_json)


def test_get_str_value():
    parse_node = TextParseNode("Diego Siciliani")
    result = parse_node.get_str_value()
    assert result == "Diego Siciliani"


def test_get_int_value():
    parse_node = TextParseNode("1454")
    result = parse_node.get_int_value()
    assert result == 1454


def test_get_bool_value():
    parse_node = TextParseNode(False)
    result = parse_node.get_bool_value()
    assert result is False


def test_get_float_value():
    parse_node = TextParseNode(44.6)
    result = parse_node.get_float_value()
    assert result == 44.6


def test_get_uuid_value():
    parse_node = TextParseNode("f58411c7-ae78-4d3c-bb0d-3f24d948de41")
    result = parse_node.get_uuid_value()
    assert result == UUID("f58411c7-ae78-4d3c-bb0d-3f24d948de41")


def test_get_datetime_value():
    parse_node = TextParseNode('2022-01-27T12:59:45.596117')
    result = parse_node.get_datetime_value()
    assert isinstance(result, datetime)


def test_get_date_value():
    parse_node = TextParseNode('2015-04-20T11:50:51Z')
    result = parse_node.get_date_value()
    assert isinstance(result, date)
    assert str(result) == '2015-04-20'


def test_get_time_value():
    parse_node = TextParseNode('2022-01-27T12:59:45.596117')
    result = parse_node.get_time_value()
    assert isinstance(result, time)
    assert str(result) == '12:59:45.596117'


def test_get_timedelta_value():
    parse_node = TextParseNode('2022-01-27T12:59:45.596117')
    result = parse_node.get_timedelta_value()
    assert isinstance(result, timedelta)
    assert str(result) == '12:59:45'


def test_get_collection_of_primitive_values():
    with pytest.raises(Exception) as e_info:
        parse_node = TextParseNode([12.1, 12.2, 12.3, 12.4, 12.5])
        result = parse_node.get_collection_of_primitive_values(float)


def test_get_bytes_value():
    parse_node = TextParseNode('U2Ftd2VsIGlzIHRoZSBiZXN0')
    result = parse_node.get_bytes_value()
    assert isinstance(result, bytes)


def test_get_collection_of_enum_values():
    with pytest.raises(Exception) as e_info:
        parse_node = TextParseNode("dunhill,oval")
        result = parse_node.get_collection_of_enum_values(OfficeLocation)


def test_get_enum_value():
    parse_node = TextParseNode("dunhill")
    result = parse_node.get_enum_value(OfficeLocation)
    assert isinstance(result, OfficeLocation)
    assert result == OfficeLocation.Dunhill


def test_get_object_value(sample_structured_data):
    with pytest.raises(Exception) as e_info:
        parse_node = TextParseNode(sample_structured_data)
        result = parse_node.get_object_value(User)


def test_get_collection_of_object_values(sample_structured_data):
    with pytest.raises(Exception) as e_info:
        parse_node = TextParseNode(sample_structured_data)
        result = parse_node.get_collection_of_object_values(User)
