from uuid import UUID
from urllib.parse import unquote_plus
import pytest

from datetime import datetime, timedelta, date, time
from kiota_serialization_form.form_serialization_writer import FormSerializationWriter
from ..helpers import TestEntity, TestEnum


@pytest.fixture
def user_1():
    user = TestEntity()
    user.created_date_time = datetime.fromisoformat("2022-01-27T12:59:45.596117")
    user.work_duration  = timedelta(seconds=7200)
    user.birthday = date(year=2000,month=9,day=4)
    user.start_work_time = time(hour=8, minute=0, second=0)
    user.id = UUID("8f841f30-e6e3-439a-a812-ebd369559c36")
    user.numbers = [TestEnum.One, TestEnum.Eight]
    user.device_names = ["device1", "device2"]
    user.additional_data = {
        "otherPhones": ["123456789","987654321"],
        "mobilePhone": None,
        "accountEnabled": False,
        "jobTitle": "Auditor",
        "intValue": 1,
        "floatValue": 3.14,
    }
    return user


def test_write_str_value():
    form_serialization_writer = FormSerializationWriter()
    form_serialization_writer.write_str_value("displayName", "Adele Vance")
    content = form_serialization_writer.get_serialized_content()
    content_string = content.decode('utf-8')
    assert content_string == "displayName=Adele+Vance"


def test_write_bool_value():
    form_serialization_writer = FormSerializationWriter()
    form_serialization_writer.write_bool_value("isActive", False)
    content = form_serialization_writer.get_serialized_content()
    content_string = content.decode('utf-8')
    assert content_string == "isActive=false"


def test_write_int_value():
    form_serialization_writer = FormSerializationWriter()
    form_serialization_writer.write_int_value("count", 0)
    content = form_serialization_writer.get_serialized_content()
    content_string = content.decode('utf-8')
    assert content_string == "count=0"


def test_write_float_value():
    form_serialization_writer = FormSerializationWriter()
    form_serialization_writer.write_float_value("gpa", 0.0)
    content = form_serialization_writer.get_serialized_content()
    content_string = content.decode('utf-8')
    assert content_string == "gpa=0.0"


def test_write_uuid_value():
    form_serialization_writer = FormSerializationWriter()
    form_serialization_writer.write_uuid_value("id", UUID("8f841f30-e6e3-439a-a812-ebd369559c36"))
    content = form_serialization_writer.get_serialized_content()
    content_string = content.decode('utf-8')
    assert content_string == "id=8f841f30-e6e3-439a-a812-ebd369559c36"
    
def test_write_uuid_value_with_valid_string():
    form_serialization_writer = FormSerializationWriter()
    form_serialization_writer.write_uuid_value("id", "8f841f30-e6e3-439a-a812-ebd369559c36")
    content = form_serialization_writer.get_serialized_content()
    content_string = content.decode('utf-8')
    assert content_string == "id=8f841f30-e6e3-439a-a812-ebd369559c36"
    
def test_write_datetime_value():
    form_serialization_writer = FormSerializationWriter()
    form_serialization_writer.write_datetime_value("updatedAt", datetime(2022, 1, 27, 12, 59, 45, 596117))
    content = form_serialization_writer.get_serialized_content()
    content_string = content.decode('utf-8')
    assert content_string == "updatedAt=2022-01-27T12%3A59%3A45.596117"
    
def test_write_datetime_value_valid_string():
    form_serialization_writer = FormSerializationWriter()
    form_serialization_writer.write_datetime_value(
        "updatedAt", "2022-01-27T12:59:45.596117"
    )
    content = form_serialization_writer.get_serialized_content()
    content_string = content.decode('utf-8')
    assert content_string == "updatedAt=2022-01-27T12%3A59%3A45.596117"
    

def test_write_timedelta_value():
    form_serialization_writer = FormSerializationWriter()
    form_serialization_writer.write_timedelta_value(
        "diff", timedelta(seconds=7200))
    content = form_serialization_writer.get_serialized_content()
    content_string = content.decode('utf-8')
    assert content_string == "diff=2%3A00%3A00"
    

def test_write_date_value():
    form_serialization_writer = FormSerializationWriter()
    form_serialization_writer.write_date_value("birthday", date(2000, 9, 4))
    content = form_serialization_writer.get_serialized_content()
    content_string = content.decode('utf-8')
    assert content_string == "birthday=2000-09-04"

def test_write_time_value():
    form_serialization_writer = FormSerializationWriter()
    form_serialization_writer.write_time_value(
        "time",
        datetime.fromisoformat('2022-01-27T12:59:45.596117').time()
    )
    content = form_serialization_writer.get_serialized_content()
    content_string = content.decode('utf-8')
    assert content_string == "time=12%3A59%3A45.596117"
    
def test_write_bytes_value():
    form_serialization_writer = FormSerializationWriter()
    form_serialization_writer.write_bytes_value(
        "message", b"Hello world"
    )
    content = form_serialization_writer.get_serialized_content()
    content_string = content.decode('utf-8')
    assert content_string == "message=SGVsbG8gd29ybGQ%3D"
    
def test_write_collection_of_primitive_values():
    form_serialization_writer = FormSerializationWriter()
    form_serialization_writer.write_collection_of_primitive_values(
        "numbers", [1, 2.0, "3"]
    )
    content = form_serialization_writer.get_serialized_content()
    content_string = content.decode('utf-8')
    assert content_string == "numbers=1&numbers=2.0&numbers=3"
    
def test_write_collection_of_enum_values():
    form_serialization_writer = FormSerializationWriter()
    form_serialization_writer.write_collection_of_enum_values(
        "numbers", [TestEnum.Four, TestEnum.Eight]
    )
    content = form_serialization_writer.get_serialized_content()
    content_string = content.decode('utf-8')
    assert content_string == "numbers=four&numbers=eight"
    
def test_write_enum_value():
    form_serialization_writer = FormSerializationWriter()
    form_serialization_writer.write_enum_value(
        "number", TestEnum.Four
    )
    content = form_serialization_writer.get_serialized_content()
    content_string = content.decode('utf-8')
    assert content_string == "number=four"
    
def test_write_enum_value_multiple():
    form_serialization_writer = FormSerializationWriter()
    form_serialization_writer.write_enum_value(
        "number", [TestEnum.Four, TestEnum.Eight]
    )
    content = form_serialization_writer.get_serialized_content()
    content_string = content.decode('utf-8')
    assert content_string == "number=four%2Ceight"
    
def test_write_collection_of_object_values():
    form_serialization_writer = FormSerializationWriter()
    with pytest.raises(Exception) as excinfo:
        form_serialization_writer.write_collection_of_object_values(
            "users", [user_1]
        )
    assert "Form serialization does not support collections." in str(excinfo.value)
    
    
def test_write_object_value(user_1):
    form_serialization_writer = FormSerializationWriter()
    form_serialization_writer.write_object_value("user", user_1)
    content = form_serialization_writer.get_serialized_content()
    content_string = content.decode('utf-8')
    assert content_string == (
        "user=id=8f841f30-e6e3-439a-a812-ebd369559c36&"
        "deviceNames=device1&deviceNames=device2&"
        "numbers=one%2Ceight&"
        "workDuration=2%3A00%3A00&"
        "birthDay=2000-09-04&"
        "startWorkTime=08%3A00%3A00&"
        "createdDateTime=2022-01-27T12%3A59%3A45.596117%2B00%3A00&"
        "otherPhones=123456789&otherPhones=987654321&"
        "jobTitle=Auditor&"
        "intValue=1&"
        "floatValue=3.14"
    )

