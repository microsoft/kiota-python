import pytest

from kiota_abstractions.request_information import RequestInformation
from kiota_abstractions.request_headers import RequestHeaders


def test_initialization():
    """Tests initialization of the RequestInformation objects
    """
    request_info = RequestInformation()
    assert request_info
    assert not request_info.path_parameters
    assert not request_info.query_parameters
    assert not request_info.request_options
    assert not request_info.url_template
    assert not request_info.http_method
    assert not request_info.content
    assert request_info.headers
    assert request_info.RAW_URL_KEY == 'request-raw-url'
    assert request_info.BINARY_CONTENT_TYPE == 'application/octet-stream'
    assert request_info.CONTENT_TYPE_HEADER == 'Content-Type'


def test_add_request_headers_null(mock_request_information):
    """Tests adding a null request header
    """
    mock_request_information.add_request_headers(None)
    assert not mock_request_information.headers.get_all()


def test_add_request_headers(mock_request_information):
    """Tests adding a request header with a string value
    """
    headers = RequestHeaders()
    headers.add("header1", "value1")
    headers.add("header2", "value2")
    mock_request_information.add_request_headers(headers)
    assert {"value1"} <= mock_request_information.headers.get("header1")
    assert {"value2"} <= mock_request_information.headers.get("header2")
    header2 = RequestHeaders()
    header2.add("header1", "value3")
    mock_request_information.add_request_headers(header2)
    assert {"value1", "value3"} <= mock_request_information.headers.get("header1")


def test_request_headers(mock_request_information):
    """Test the final request headers
    """
    headers = RequestHeaders()
    headers.add("header1", ["value1", "value2"])
    headers.add("header2", ["value3", "value4"])
    mock_request_information.add_request_headers(headers)
    assert "value1" in mock_request_information.request_headers["header1"]
    assert "value2" in mock_request_information.request_headers["header1"]
    assert "value3" in mock_request_information.request_headers["header2"]
    assert "value4" in mock_request_information.request_headers["header2"]
    headers2 = RequestHeaders()
    headers2.add("header1", ["value1", "value2", "value5", "value6"])
    mock_request_information.add_request_headers(headers2)
    assert "value5" in mock_request_information.request_headers["header1"]
    assert "value6" in mock_request_information.request_headers["header1"]

    # Ensure duplicates are removed
    assert len(mock_request_information.request_headers["header1"]
               ) == len("value1, value2, value5, value6")
    assert len(mock_request_information.request_headers["header2"]) == len("value3, value4")
    assert "value1" in mock_request_information.request_headers["header1"]
    assert "value1" not in mock_request_information.request_headers["header2"]
    assert "value3" in mock_request_information.request_headers["header2"]
    assert "value4" in mock_request_information.request_headers["header2"]

def test_remove_request_headers(mock_request_information):
    """Tests removing a request header
    """
    headers = RequestHeaders()
    headers.add("header1", "value1")
    headers.add("header2", "value2")
    mock_request_information.add_request_headers(headers)
    assert mock_request_information.headers.get("header1") == {"value1"}
    assert mock_request_information.headers.get("header2") == {"value2"}
    mock_request_information.remove_request_headers("header1")
    mock_request_information.remove_request_headers("header3")
    assert 'header1' not in mock_request_information.request_headers
    assert mock_request_information.headers.try_get("header2") == {"value2"}


def test_set_stream_content(mock_request_information):
    """Tests setting the stream content
    """
    mock_request_information.set_stream_content(b'stream')
    assert mock_request_information.content == b'stream'
    assert mock_request_information.headers.get("content-type") == {"application/octet-stream"}
