import io
from unittest.mock import Mock, call

import pytest

from kiota_abstractions.multipart_body import MultipartBody
from kiota_abstractions.serialization import SerializationWriter

from .conftest import MockEntity


def test_default_boundary_is_unique_per_instance():
    first = MultipartBody()
    second = MultipartBody()

    assert first.boundary != second.boundary


def test_custom_boundary_is_preserved():
    multipart = MultipartBody(boundary="custom-boundary")

    assert multipart.boundary == "custom-boundary"


def test_defensive():
    """Tests initialization of MultipartBody objects
    """
    multipart = MultipartBody()
    with pytest.raises(ValueError) as excinfo:
        multipart.add_or_replace_part(None, "text/plain", "Hello, World!")
    assert "Part name cannot be null" in str(excinfo.value)
    with pytest.raises(ValueError) as excinfo:
        multipart.add_or_replace_part("text", None, "Hello, World!")
    assert "Content type cannot be null" in str(excinfo.value)
    with pytest.raises(ValueError) as excinfo:
        multipart.add_or_replace_part("text", "text/plain", None)
    assert "Part value cannot be null" in str(excinfo.value)
    with pytest.raises(ValueError) as excinfo:
        multipart.get_part_value(None)
    assert "Part name cannot be null" in str(excinfo.value)
    with pytest.raises(ValueError) as excinfo:
        multipart.get_part_value("")
    assert "Part name cannot be null" in str(excinfo.value)
    with pytest.raises(ValueError) as excinfo:
        multipart.remove_part(None)
    assert "Part name cannot be null" in str(excinfo.value)
    with pytest.raises(ValueError) as excinfo:
        multipart.remove_part("")
    assert "Part name cannot be null" in str(excinfo.value)
    with pytest.raises(ValueError) as excinfo:
        multipart.serialize(None)
    assert "Serialization writer cannot be null" in str(excinfo.value)


def test_add_or_replace_part():
    """Tests adding or replacing a part in the multipart body
    """
    multipart = MultipartBody()
    multipart.add_or_replace_part("text", "text/plain", "Hello, World!")
    assert multipart.get_part_value("text") == "Hello, World!"
    multipart.add_or_replace_part("text", "text/plain", "Hello, World! 2")
    assert multipart.get_part_value("text") == "Hello, World! 2"


def test_remove_part():
    """Tests removing a part from the multipart body
    """
    multipart = MultipartBody()
    multipart.add_or_replace_part("text", "text/plain", "Hello, World!")
    assert multipart.get_part_value("text") == "Hello, World!"
    assert multipart.remove_part("text")
    assert not multipart.get_part_value("text")
    assert not multipart.remove_part("text")


def test_add_or_replace_part_empty_values():
    """Tests adding empty byte and string parts to the multipart body."""
    multipart = MultipartBody()
    multipart.add_or_replace_part("empty_bytes", "application/octet-stream", b"")
    assert multipart.get_part_value("empty_bytes") == b""

    multipart.add_or_replace_part("empty_str", "text/plain", "")
    assert multipart.get_part_value("empty_str") == ""

    multipart.add_or_replace_part("empty_stream", "application/octet-stream", io.BytesIO(b""))
    stream_val = multipart.get_part_value("empty_stream")
    assert isinstance(stream_val, io.IOBase)

    mock_writer = Mock(spec=SerializationWriter)
    multipart.serialize(mock_writer)

    # Verify that empty payloads reach the serialization writer
    assert mock_writer.write_bytes_value.call_count == 3
    mock_writer.write_bytes_value.assert_has_calls([call("", b""), call("", b""), call("", b"")])


def test_content_disposition():
    multipart = MultipartBody()
    disp_with_file = multipart._get_content_disposition(
        "doc", ("application/pdf", b"data", "doc.pdf")
    )
    assert disp_with_file == 'form-data; name="doc"; filename="doc.pdf"'

    disp_without_file = multipart._get_content_disposition("text", ("text/plain", "hello", None))
    assert disp_without_file == 'form-data; name="text"'


def test_serialize_without_request_adapter():
    multipart = MultipartBody()
    multipart.add_or_replace_part("text", "text/plain", "Hello")
    multipart.add_or_replace_part("binary", "application/octet-stream", b"123")
    multipart.add_or_replace_part("stream", "application/octet-stream", io.BytesIO(b"456"))

    mock_writer = Mock(spec=SerializationWriter)
    multipart.serialize(mock_writer)
    assert mock_writer.write_str_value.called
    assert mock_writer.write_bytes_value.called


def test_serialize_parsable_requires_request_adapter():
    multipart = MultipartBody()
    multipart.add_or_replace_part("entity", "application/json", MockEntity())

    mock_writer = Mock(spec=SerializationWriter)
    with pytest.raises(ValueError) as excinfo:
        multipart.serialize(mock_writer)
    assert "Request adapter or serialization writer factory cannot be null" in str(excinfo.value)
