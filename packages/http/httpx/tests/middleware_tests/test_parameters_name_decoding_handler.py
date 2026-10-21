import pytest

import httpx
from kiota_http.middleware.options import ParametersNameDecodingHandlerOption
from kiota_http.middleware.parameters_name_decoding_handler import (
    PARAMETERS_NAME_DECODING_KEY,
    ParametersNameDecodingHandler,
)

OPTION_KEY = "ParametersNameDecodingHandlerOption"


class MockSpan:

    def __init__(self):
        self.end_called = 0
        self.attributes = {}

    def set_attribute(self, key, value):
        self.attributes[key] = value

    def end(self):
        self.end_called += 1


def test_no_config():
    """
    Test that default values are used if no custom confguration is passed
    """
    handler = ParametersNameDecodingHandler()
    assert handler.options.enabled is True
    assert handler.options.characters_to_decode == [".", "-", "~", "$"]
    assert handler.options.get_key() == OPTION_KEY


def test_custom_options():
    """
    Test that default configuration is overrriden if custom configuration is provided
    """
    options = ParametersNameDecodingHandlerOption(enable=False, characters_to_decode=[".", "-"])
    handler = ParametersNameDecodingHandler(options)

    assert handler.options.enabled is not True
    assert "$" not in handler.options.characters_to_decode
    assert handler.options.get_key() == OPTION_KEY


@pytest.mark.asyncio
async def test_decodes_query_parameter_names_only():
    """
    Test that only query parameter names are decoded
    """
    encoded_decoded = [
        (
            "http://localhost?%24select=diplayName&api%2Dversion=2",
            "http://localhost?$select=diplayName&api-version=2"
        ),
        (
            "http://localhost?%24select=diplayName&api%7Eversion=2",
            "http://localhost?$select=diplayName&api~version=2"
        ),
        (
            "http://localhost?%24select=diplayName&api%2Eversion=2",
            "http://localhost?$select=diplayName&api.version=2"
        ),
        (
            "http://localhost:888?%24select=diplayName&api%2Dversion=2",
            "http://localhost:888?$select=diplayName&api-version=2"
        ),
        ("http://localhost", "http://localhost"),
        ("https://google.com/?q=1%2b2", "https://google.com/?q=1%2b2"),
        ("https://google.com/?q=M%26A", "https://google.com/?q=M%26A"),
        ("https://google.com/?q=1%2B2", "https://google.com/?q=1%2B2"),  # Values are not decoded
        ("https://google.com/?q=M%26A", "https://google.com/?q=M%26A"),  # Values are not decoded
        ("https://google.com/?q%2D1=M%26A",
         "https://google.com/?q-1=M%26A"),  # Values are not decoded but params are
        ("https://google.com/?q%2D1&q=M%26A=M%26A",
         "https://google.com/?q-1&q=M%26A=M%26A"),  # Values are not decoded but params are
        (
            "https://graph.microsoft.com?%24count=true&query=%24top&created%2Din=2022-10-05&q=1%2b2&q2=M%26A&subject%2Ename=%7eWelcome&%24empty",
            "https://graph.microsoft.com?$count=true&query=%24top&created-in=2022-10-05&q=1%2b2&q2=M%26A&subject.name=%7eWelcome&$empty"
        )
    ]

    def request_handler(request: httpx.Request):
        return httpx.Response(200, json={"text": "Hello, world!"})

    handler = ParametersNameDecodingHandler()
    for encoded, decoded in encoded_decoded:
        request = httpx.Request('GET', encoded)
        mock_transport = httpx.MockTransport(request_handler)
        resp = await handler.send(request, mock_transport)
        assert str(resp.request.url).casefold() == decoded.casefold()


def test_default_characters_to_decode_are_not_shared():
    ParametersNameDecodingHandlerOption().characters_to_decode.append("+")
    assert ParametersNameDecodingHandlerOption().characters_to_decode == [".", "-", "~", "$"]


@pytest.mark.asyncio
async def test_send_request_none_raises_type_error():
    handler = ParametersNameDecodingHandler()
    with pytest.raises(TypeError, match="request cannot be null"):
        await handler.send(None, None)


@pytest.mark.asyncio
async def test_decoding_preserves_values_matching_parameter_name():

    def request_handler(request: httpx.Request):
        return httpx.Response(200, json={"text": "Hello, world!"})

    handler = ParametersNameDecodingHandler()
    request = httpx.Request('GET', "https://example.com/api?query=%24select&%24select=name")
    mock_transport = httpx.MockTransport(request_handler)
    resp = await handler.send(request, mock_transport)
    assert str(resp.request.url) == "https://example.com/api?query=%24select&$select=name"


@pytest.mark.asyncio
async def test_decodes_lowercase_percent_encoding():

    def request_handler(request: httpx.Request):
        return httpx.Response(200, json={"text": "Hello, world!"})

    handler = ParametersNameDecodingHandler()
    request = httpx.Request(
        'GET', "https://example.com/api?api%2dversion=1&param%2evalue=2&flag%7etest=3"
    )
    mock_transport = httpx.MockTransport(request_handler)
    resp = await handler.send(request, mock_transport)
    assert str(
        resp.request.url
    ) == "https://example.com/api?api-version=1&param.value=2&flag~test=3"


@pytest.mark.asyncio
async def test_decoding_preserves_url_path():

    def request_handler(request: httpx.Request):
        return httpx.Response(200, json={"text": "Hello, world!"})

    handler = ParametersNameDecodingHandler()
    request = httpx.Request('GET', "https://example.com/api/%24select=name/items?%24select=name")
    mock_transport = httpx.MockTransport(request_handler)
    resp = await handler.send(request, mock_transport)
    assert str(resp.request.url) == "https://example.com/api/%24select=name/items?$select=name"
    assert b"/api/%24select=name/items" in resp.request.url.raw_path
    assert resp.request.url.query == b"$select=name"


@pytest.mark.asyncio
async def test_span_lifecycle_active_during_send_and_ends_on_success(monkeypatch):
    mock_span = MockSpan()
    handler = ParametersNameDecodingHandler()
    monkeypatch.setattr(handler, "_create_observability_span", lambda *_: mock_span)

    transport_called = False

    def request_handler(request: httpx.Request):
        nonlocal transport_called
        transport_called = True
        assert mock_span.end_called == 0
        return httpx.Response(200, json={"text": "Hello, world!"})

    request = httpx.Request("GET", "https://example.com/api?%24select=name")
    resp = await handler.send(request, httpx.MockTransport(request_handler))

    assert transport_called is True
    assert mock_span.end_called == 1
    assert mock_span.attributes.get(PARAMETERS_NAME_DECODING_KEY) is True
    assert str(resp.request.url) == "https://example.com/api?$select=name"


@pytest.mark.asyncio
async def test_span_lifecycle_ends_and_exception_propagates_on_transport_failure(monkeypatch):
    mock_span = MockSpan()
    handler = ParametersNameDecodingHandler()
    monkeypatch.setattr(handler, "_create_observability_span", lambda *_: mock_span)

    transport_called = False

    def request_handler(request: httpx.Request):
        nonlocal transport_called
        transport_called = True
        assert mock_span.end_called == 0
        raise httpx.ReadError("transport connection interrupted")

    request = httpx.Request("GET", "https://example.com/api?%24select=name")
    transport = httpx.MockTransport(request_handler)
    with pytest.raises(httpx.ReadError, match="transport connection interrupted"):
        await handler.send(request, transport)

    assert transport_called is True
    assert mock_span.end_called == 1
