import pytest

from kiota_abstractions.base_request_builder import BaseRequestBuilder


def test_initialization(mock_request_adapter):
    request_builder = BaseRequestBuilder(mock_request_adapter, "{+baseurl}", None)
    assert request_builder.request_adapter == mock_request_adapter
    assert request_builder.url_template == "{+baseurl}"
    assert request_builder.path_parameters == {}


def test_initialization_with_no_adapter_raises_exception(mock_request_adapter):
    with pytest.raises(TypeError) as excinfo:
        request_builder = BaseRequestBuilder(None, "{+baseurl}", None)
    assert "request_adapter cannot be null." in str(excinfo.value)


def test_initialization_with_no_url_template_raises_exception(mock_request_adapter):
    with pytest.raises(TypeError) as excinfo:
        request_builder = BaseRequestBuilder(mock_request_adapter, None, None)
    assert "url_template cannot be null." in str(excinfo.value)


def test_initialization_with_empty_url_template_valid(mock_request_adapter):
    request_builder = BaseRequestBuilder(mock_request_adapter, "", None)
    assert request_builder.request_adapter == mock_request_adapter
    assert request_builder.url_template == ""
    assert request_builder.path_parameters == {}


def test_initialization_with_path_parameters(mock_request_adapter):
    request_builder = BaseRequestBuilder(
        mock_request_adapter, "{+baseurl}", {"baseurl": "https://example.com"}
    )
    assert request_builder.request_adapter == mock_request_adapter
    assert request_builder.url_template == "{+baseurl}"
    assert request_builder.path_parameters == {"baseurl": "https://example.com"}


def test_initialization_with_path_parameters_as_string_sets_raw_url(mock_request_adapter):
    request_builder = BaseRequestBuilder(mock_request_adapter, "{+baseurl}", "https://example.com")
    assert request_builder.request_adapter == mock_request_adapter
    assert request_builder.url_template == "{+baseurl}"
    assert request_builder.path_parameters == {"request-raw-url": "https://example.com"}
