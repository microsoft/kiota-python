from datetime import date, datetime, time, timedelta
from unittest.mock import Mock
from uuid import UUID

import pytest

from kiota_serialization_multipart.multipart_serialization_writer import (
    MultipartSerializationWriter,
)

from ..helpers import TestEntity, TestEnum


def test_not_implemented():
    writer = MultipartSerializationWriter()
    with pytest.raises(NotImplementedError):
        writer.write_bool_value("isActive", False)
    with pytest.raises(NotImplementedError):
        writer.write_date_value("birthday", date(2000, 9, 4))
    with pytest.raises(NotImplementedError):
        writer.write_datetime_value("updatedAt", datetime(2022, 1, 27, 12, 59, 45, 596117))
    with pytest.raises(NotImplementedError):
        writer.write_time_value("time", time(hour=12, minute=59, second=45, microsecond=596117))
    with pytest.raises(NotImplementedError):
        writer.write_timedelta_value("diff", timedelta(seconds=7200))
    with pytest.raises(NotImplementedError):
        writer.write_enum_value("number", TestEnum.Four)
    with pytest.raises(NotImplementedError):
        writer.write_float_value("gpa", 0.0)
    with pytest.raises(NotImplementedError):
        writer.write_int_value("count", 0)
    with pytest.raises(NotImplementedError):
        writer.write_uuid_value("id", UUID("8f841f30-e6e3-439a-a812-ebd369559c36"))
    with pytest.raises(NotImplementedError):
        writer.write_collection_of_enum_values("numbers", [TestEnum.Four, TestEnum.Eight])
    with pytest.raises(NotImplementedError):
        writer.write_collection_of_object_values("users", [TestEntity()])
    with pytest.raises(NotImplementedError):
        writer.write_collection_of_primitive_values("numbers", [1, 2.0, "3"])


def test_write_string_value():
    serialization_writer = MultipartSerializationWriter()
    serialization_writer.write_str_value("message", "Hello world")
    content = serialization_writer.get_serialized_content()
    content_string = content.decode('utf-8')
    assert content_string == "message: Hello world\r\n"


def test_write_bytes_value_bytes():
    serialization_writer = MultipartSerializationWriter()
    serialization_writer.write_bytes_value("", b"Hello world")
    content = serialization_writer.get_serialized_content()
    content_string = content.decode('utf-8')
    assert content_string == "Hello world"


def test_write_object_value_raises_exception_on_parseable_object():
    serialization_writer = MultipartSerializationWriter()
    with pytest.raises(ValueError) as excinfo:
        serialization_writer.write_object_value("user", TestEntity())
    assert "Expected a MultipartBody instance but got" in str(excinfo.value)


def test_write_object_value(
    user_1, mock_request_adapter, mock_serialization_writer_factory, mock_multipart_body
):
    mock_request_adapter.get_serialization_writer_factory = Mock(
        return_value=mock_serialization_writer_factory
    )
    mock_multipart_body.request_adapter = mock_request_adapter
    mock_multipart_body.add_or_replace_part("test user", "application/json", user_1)
    mock_multipart_body.add_or_replace_part("img", "application/octet-stream", b"Hello world")

    serialization_writer = MultipartSerializationWriter()
    serialization_writer.write_object_value("", mock_multipart_body, None)
    content = serialization_writer.get_serialized_content()
    content_string = content.decode('utf-8')
    assert content_string == f'--{mock_multipart_body.boundary}' + '\r\nContent-Type: application/json\r\nContent-Disposition: form-data; name="test user"\r\n\r\n{"id": "eac79bd3-fd08-4abf-9df2-2565cf3a3845", "workDuration": "2:00:00", "birthDay": "2017-09-04", "startWorkTime": "00:00:00", "createdDateTime": "2022-01-27T12:59:45", "businessPhones": ["+1 412 555 0109"], "mobilePhone": null, "accountEnabled": false, "jobTitle": "Auditor", "manager": {"id": "eac79bd3-fd08-4abf-9df2-2565cf3a3845"}}\r\n' + f'--{mock_multipart_body.boundary}' + '\r\nContent-Type: application/octet-stream\r\nContent-Disposition: form-data; name="img"\r\n\r\nHello world\r\n' + f'--{mock_multipart_body.boundary}--\r\n'


def test_write_object_value_inverted(
    user_1, mock_request_adapter, mock_serialization_writer_factory, mock_multipart_body
):
    mock_request_adapter.get_serialization_writer_factory = Mock(
        return_value=mock_serialization_writer_factory
    )
    mock_multipart_body.request_adapter = mock_request_adapter
    mock_multipart_body.add_or_replace_part("img", "application/octet-stream", b"Hello world")
    mock_multipart_body.add_or_replace_part("test user", "application/json", user_1)

    serialization_writer = MultipartSerializationWriter()
    serialization_writer.write_object_value("", mock_multipart_body, None)
    content = serialization_writer.get_serialized_content()
    content_string = content.decode('utf-8')
    assert content_string == f'--{mock_multipart_body.boundary}' + '\r\nContent-Type: application/octet-stream\r\nContent-Disposition: form-data; name="img"\r\n\r\nHello world\r\n' + f'--{mock_multipart_body.boundary}' + '\r\nContent-Type: application/json\r\nContent-Disposition: form-data; name="test user"\r\n\r\n{"id": "eac79bd3-fd08-4abf-9df2-2565cf3a3845", "workDuration": "2:00:00", "birthDay": "2017-09-04", "startWorkTime": "00:00:00", "createdDateTime": "2022-01-27T12:59:45", "businessPhones": ["+1 412 555 0109"], "mobilePhone": null, "accountEnabled": false, "jobTitle": "Auditor", "manager": {"id": "eac79bd3-fd08-4abf-9df2-2565cf3a3845"}}\r\n' + f'--{mock_multipart_body.boundary}--\r\n'


def test_write_object_value_with_filename(
    user_1, mock_request_adapter, mock_serialization_writer_factory, mock_multipart_body
):
    mock_request_adapter.get_serialization_writer_factory = Mock(
        return_value=mock_serialization_writer_factory
    )
    mock_multipart_body.request_adapter = mock_request_adapter
    mock_multipart_body.add_or_replace_part("test user", "application/json", user_1)
    mock_multipart_body.add_or_replace_part(
        "file", "application/octet-stream", b"Hello world", "file.txt"
    )

    serialization_writer = MultipartSerializationWriter()
    serialization_writer.write_object_value("", mock_multipart_body, None)
    content = serialization_writer.get_serialized_content()
    content_string = content.decode('utf-8')
    assert content_string == f'--{mock_multipart_body.boundary}' + '\r\nContent-Type: application/json\r\nContent-Disposition: form-data; name="test user"\r\n\r\n{"id": "eac79bd3-fd08-4abf-9df2-2565cf3a3845", "workDuration": "2:00:00", "birthDay": "2017-09-04", "startWorkTime": "00:00:00", "createdDateTime": "2022-01-27T12:59:45", "businessPhones": ["+1 412 555 0109"], "mobilePhone": null, "accountEnabled": false, "jobTitle": "Auditor", "manager": {"id": "eac79bd3-fd08-4abf-9df2-2565cf3a3845"}}\r\n' + f'--{mock_multipart_body.boundary}' + '\r\nContent-Type: application/octet-stream\r\nContent-Disposition: form-data; name="file"; filename="file.txt"\r\n\r\nHello world\r\n' + f'--{mock_multipart_body.boundary}--\r\n'


def test_write_object_value_with_string_part(
    mock_request_adapter, mock_serialization_writer_factory, mock_multipart_body
):
    mock_request_adapter.get_serialization_writer_factory = Mock(
        return_value=mock_serialization_writer_factory
    )
    mock_multipart_body.request_adapter = mock_request_adapter
    mock_multipart_body.add_or_replace_part("message", "text/plain", "Hello world")

    serialization_writer = MultipartSerializationWriter()
    serialization_writer.write_object_value("", mock_multipart_body, None)
    content = serialization_writer.get_serialized_content()
    content_string = content.decode('utf-8')
    assert content_string == f'--{mock_multipart_body.boundary}' + '\r\nContent-Type: text/plain\r\nContent-Disposition: form-data; name="message"\r\n\r\nHello world\r\n' + f'--{mock_multipart_body.boundary}--\r\n'


def test_write_object_value_with_multiple_string_parts(
    mock_request_adapter, mock_serialization_writer_factory, mock_multipart_body
):
    mock_request_adapter.get_serialization_writer_factory = Mock(
        return_value=mock_serialization_writer_factory
    )
    mock_multipart_body.request_adapter = mock_request_adapter
    mock_multipart_body.add_or_replace_part("message1", "text/plain", "Hello world")
    mock_multipart_body.add_or_replace_part("message2", "text/plain", "Goodbye world")

    serialization_writer = MultipartSerializationWriter()
    serialization_writer.write_object_value("", mock_multipart_body, None)
    content = serialization_writer.get_serialized_content()
    content_string = content.decode('utf-8')
    assert content_string == f'--{mock_multipart_body.boundary}' + '\r\nContent-Type: text/plain\r\nContent-Disposition: form-data; name="message1"\r\n\r\nHello world\r\n' + f'--{mock_multipart_body.boundary}' + '\r\nContent-Type: text/plain\r\nContent-Disposition: form-data; name="message2"\r\n\r\nGoodbye world\r\n' + f'--{mock_multipart_body.boundary}--\r\n'


def test_write_str_value_omits_nil_value():
    serialization_writer = MultipartSerializationWriter()
    serialization_writer.write_str_value("Content-Type", None)
    content = serialization_writer.get_serialized_content()
    assert content == b""


def test_write_str_value_omits_both_nil():
    serialization_writer = MultipartSerializationWriter()
    serialization_writer.write_str_value(None, None)
    content = serialization_writer.get_serialized_content()
    assert content == b""


def test_write_object_value_handles_none_gracefully():
    serialization_writer = MultipartSerializationWriter()
    serialization_writer.write_object_value("", None)
    content = serialization_writer.get_serialized_content()
    assert content == b""


def test_write_object_value_with_additional_values_to_merge(
    user_1, mock_request_adapter, mock_serialization_writer_factory
):
    import email
    from email.policy import default

    from kiota_abstractions.multipart_body import MultipartBody

    mock_request_adapter.get_serialization_writer_factory = Mock(
        return_value=mock_serialization_writer_factory
    )

    body1 = MultipartBody()
    body1.boundary = "body1-boundary"
    body1.request_adapter = mock_request_adapter
    body1.add_or_replace_part("part1", "text/plain", "First part")

    body2 = MultipartBody()
    body2.boundary = "body2-boundary"
    body2.request_adapter = mock_request_adapter
    body2.add_or_replace_part("part2", "text/plain", "Second part")

    before_calls = []
    after_calls = []

    serialization_writer = MultipartSerializationWriter()
    serialization_writer.on_before_object_serialization = lambda obj: before_calls.append(obj)
    serialization_writer.on_after_object_serialization = lambda obj: after_calls.append(obj)

    serialization_writer.write_object_value("", body1, body2)
    raw_content = serialization_writer.get_serialized_content()
    content = raw_content.decode("utf-8")

    # Assert callbacks were preserved for each object
    assert before_calls == [body1, body2]
    assert after_calls == [body1, body2]

    # Verify serialized under single boundary with a single closing delimiter
    boundary = body1.boundary
    assert f"--{boundary}\r\n" in content
    assert f"--{body2.boundary}" not in content
    assert content.endswith(f"--{boundary}--\r\n")
    assert content.count(f"--{boundary}--") == 1

    # Verify both parts can be parsed by MIME parser under one boundary
    mime_message = email.message_from_bytes(
        f"Content-Type: multipart/form-data; boundary={boundary}\r\n\r\n".encode("utf-8") +
        raw_content,
        policy=default,
    )
    assert mime_message.is_multipart()
    parts = mime_message.get_payload()
    assert len(parts) == 2
    assert parts[0].get_param("name", header="content-disposition") == "part1"
    assert parts[0].get_content_type() == "text/plain"
    assert parts[0].get_content().strip() == "First part"
    assert parts[1].get_param("name", header="content-disposition") == "part2"
    assert parts[1].get_content_type() == "text/plain"
    assert parts[1].get_content().strip() == "Second part"


def test_write_object_value_with_invalid_additional_value_raises():
    from kiota_abstractions.multipart_body import MultipartBody

    body = MultipartBody()
    serialization_writer = MultipartSerializationWriter()
    with pytest.raises(ValueError) as excinfo:
        serialization_writer.write_object_value("", body, TestEntity())
    assert "Expected a MultipartBody instance but got" in str(excinfo.value)
