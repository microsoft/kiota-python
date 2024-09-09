from uuid import UUID
from unittest.mock import Mock
import pytest

from datetime import datetime, timedelta, date, time
from kiota_abstractions.multipart_body import MultipartBody
from kiota_abstractions.request_adapter import RequestAdapter
from kiota_serialization_json.json_serialization_writer_factory import JsonSerializationWriterFactory
from kiota_serialization_multipart.multipart_serialization_writer import MultipartSerializationWriter
from .helpers import TestEntity, TestEnum


@pytest.fixture
def user_1():
    user = TestEntity()
    user.created_date_time = datetime(2022, 1, 27, 12, 59, 45)
    user.work_duration  = timedelta(seconds=7200)
    user.birthday = date(year=2017,month=9,day=4)
    user.start_work_time = time(hour=0, minute=0, second=0)
    user.id = UUID("eac79bd3-fd08-4abf-9df2-2565cf3a3845")
    user.additional_data = {
        "businessPhones": ["+1 412 555 0109"],
        "mobilePhone": None,
        "accountEnabled": False,
        "jobTitle": "Auditor",
        "manager": TestEntity(id=UUID("eac79bd3-fd08-4abf-9df2-2565cf3a3845")),
    }
    return user

@pytest.fixture
def mock_request_adapter():
    request_adapter = Mock(spec=RequestAdapter)
    return request_adapter

@pytest.fixture
def mock_serialization_writer_factory():
    return JsonSerializationWriterFactory()

@pytest.fixture
def mock_multipart_body():
    return MultipartBody()