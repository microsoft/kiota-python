from uuid import UUID

import pytest
from dateutil import parser
from kiota_abstractions.serialization import Parsable, SerializationWriter

from kiota_serialization_text.text_serialization_writer import TextSerializationWriter

from ..helpers import OfficeLocation, User


@pytest.fixture
def user_1():
    user = User()
    user.age = 31
    user.is_active = True
    user.display_name = "Jane Doe"
    return user


@pytest.fixture
def user_2():
    user = User()
    user.age = 32
    user.is_active = False
    user.display_name = "John Doe"
    return user


def test_write_str_value():
    text_serialization_writer = TextSerializationWriter()
    text_serialization_writer.write_str_value("", "Adele Vance")
    content = text_serialization_writer.get_serialized_content()
    content_string = content.decode('utf-8')
    assert content_string == 'Adele Vance'


def test_write_str_value_with_key():
    with pytest.raises(Exception) as e_info:
        text_serialization_writer = TextSerializationWriter()
        text_serialization_writer.write_str_value("displayName", "Adele Vance")


def test_write_bool_value():
    text_serialization_writer = TextSerializationWriter()
    text_serialization_writer.write_bool_value(None, True)
    content = text_serialization_writer.get_serialized_content()
    content_string = content.decode('utf-8')
    assert content_string == 'true'


def test_write_bool_value_with_key():
    with pytest.raises(Exception) as e_info:
        text_serialization_writer = TextSerializationWriter()
        text_serialization_writer.write_bool_value("isActive", True)


def test_write_int_value():
    text_serialization_writer = TextSerializationWriter()
    text_serialization_writer.write_int_value("", 28192199291929192)
    content = text_serialization_writer.get_serialized_content()
    content_string = content.decode('utf-8')
    assert content_string == '28192199291929192'


def test_write_int_value_with_key():
    with pytest.raises(Exception) as e_info:
        text_serialization_writer = TextSerializationWriter()
        text_serialization_writer.write_int_value("timestamp", 28192199291929192)


def test_write_float_value():
    text_serialization_writer = TextSerializationWriter()
    text_serialization_writer.write_float_value("", 3.2)
    content = text_serialization_writer.get_serialized_content()
    content_string = content.decode('utf-8')
    assert content_string == '3.2'


def test_write_float_value_with_key():
    with pytest.raises(Exception) as e_info:
        text_serialization_writer = TextSerializationWriter()
        text_serialization_writer.write_float_value("gpa", 3.2)


def test_write_uuid_value():
    text_serialization_writer = TextSerializationWriter()
    text_serialization_writer.write_uuid_value("", UUID("8f841f30-e6e3-439a-a812-ebd369559c36"))
    content = text_serialization_writer.get_serialized_content()
    content_string = content.decode('utf-8')
    assert content_string == "8f841f30-e6e3-439a-a812-ebd369559c36"


def test_write_uuid_value_with_key():
    with pytest.raises(Exception) as e_info:
        text_serialization_writer = TextSerializationWriter()
        text_serialization_writer.write_uuid_value(
            "id", UUID("8f841f30-e6e3-439a-a812-ebd369559c36")
        )


def test_write_datetime_value():
    text_serialization_writer = TextSerializationWriter()
    text_serialization_writer.write_datetime_value("", parser.parse('2022-01-27T12:59:45.596117'))
    content = text_serialization_writer.get_serialized_content()
    content_string = content.decode('utf-8')
    assert content_string == "2022-01-27T12:59:45.596117"


def test_write_datetime_value_with_key():
    with pytest.raises(Exception) as e_info:
        text_serialization_writer = TextSerializationWriter()
        text_serialization_writer.write_datetime_value(
            "updatedAt", parser.parse('2022-01-27T12:59:45.596117')
        )


def test_write_timedelta_value():
    text_serialization_writer = TextSerializationWriter()
    text_serialization_writer.write_timedelta_value(
        "",
        parser.parse('2022-01-27T12:59:45.596117') - parser.parse('2022-01-27T10:59:45.596117')
    )
    content = text_serialization_writer.get_serialized_content()
    content_string = content.decode('utf-8')
    assert content_string == "2:00:00"


def test_write_timedelta_value_with_key():
    with pytest.raises(Exception) as e_info:
        text_serialization_writer = TextSerializationWriter()
        text_serialization_writer.write_timedelta_value(
            "diff",
            parser.parse('2022-01-27T12:59:45.596117') - parser.parse('2022-01-27T10:59:45.596117')
        )


def test_write_date_value():
    text_serialization_writer = TextSerializationWriter()
    text_serialization_writer.write_date_value("", parser.parse("2000-09-04").date())
    content = text_serialization_writer.get_serialized_content()
    content_string = content.decode('utf-8')
    assert content_string == "2000-09-04"


def test_write_date_value_with_key():
    with pytest.raises(Exception) as e_info:
        text_serialization_writer = TextSerializationWriter()
        text_serialization_writer.write_date_value("birthday", parser.parse("2000-09-04").date())


def test_write_time_value():
    text_serialization_writer = TextSerializationWriter()
    text_serialization_writer.write_time_value(
        "",
        parser.parse('2022-01-27T12:59:45.596117').time()
    )
    content = text_serialization_writer.get_serialized_content()
    content_string = content.decode('utf-8')
    assert content_string == "12:59:45.596117"


def test_write_time_value_with_key():
    with pytest.raises(Exception) as e_info:
        text_serialization_writer = TextSerializationWriter()
        text_serialization_writer.write_time_value(
            "time",
            parser.parse('2022-01-27T12:59:45.596117').time()
        )


def test_write_collection_of_primitive_values():
    with pytest.raises(Exception) as e_info:
        text_serialization_writer = TextSerializationWriter()
        text_serialization_writer.write_collection_of_primitive_values(
            "businessPhones", ["+1 412 555 0109", 1]
        )


def test_write_collection_of_object_values(user_1, user_2):
    with pytest.raises(Exception) as e_info:
        text_serialization_writer = TextSerializationWriter()
        text_serialization_writer.write_collection_of_object_values("users", [user_1, user_2])


def test_write_collection_of_enum_values():
    with pytest.raises(Exception) as e_info:
        text_serialization_writer = TextSerializationWriter()
        text_serialization_writer.write_collection_of_enum_values(
            "officeLocation", [OfficeLocation.Dunhill, OfficeLocation.Oval]
        )


def test_write_object_value(user_1):
    with pytest.raises(Exception) as e_info:
        text_serialization_writer = TextSerializationWriter()
        text_serialization_writer.write_object_value("user1", user_1)


def test_write_enum_value():
    text_serialization_writer = TextSerializationWriter()
    text_serialization_writer.write_enum_value("", OfficeLocation.Dunhill)
    content = text_serialization_writer.get_serialized_content()
    content_string = content.decode('utf-8')
    assert content_string == "dunhill"


def test_write_enum_value_with_key():
    with pytest.raises(Exception) as e_info:
        text_serialization_writer = TextSerializationWriter()
        text_serialization_writer.write_enum_value("officeLocation", OfficeLocation.Dunhill)


def test_write_null_value():
    text_serialization_writer = TextSerializationWriter()
    text_serialization_writer.write_null_value("")
    content = text_serialization_writer.get_serialized_content()
    content_string = content.decode('utf-8')
    assert content_string == 'null'


def test_write_null_value_with_key():
    with pytest.raises(Exception) as e_info:
        text_serialization_writer = TextSerializationWriter()
        text_serialization_writer.write_null_value("mobilePhone")


def test_write_additional_data_value():
    with pytest.raises(Exception) as e_info:
        text_serialization_writer = TextSerializationWriter()
        text_serialization_writer.write_additional_data_value(
            {
                "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users/$entity",
                "businessPhones": ["+1 205 555 0108"],
            }
        )
