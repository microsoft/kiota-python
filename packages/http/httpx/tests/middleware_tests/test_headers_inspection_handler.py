import pytest
from kiota_abstractions.headers_collection import HeadersCollection

import httpx
from kiota_http.middleware.headers_inspection_handler import HeadersInspectionHandler
from kiota_http.middleware.middleware import REQUEST_OPTIONS_KEY, BaseMiddleware
from kiota_http.middleware.options.headers_inspection_handler_option import (
    HeadersInspectionHandlerOption,
)


def test_no_config():
    """
    Ensures the Header Inspection defaults are set.
    """
    options = HeadersInspectionHandlerOption()
    assert options.inspect_request_headers
    assert options.inspect_response_headers
    assert isinstance(options.request_headers, HeadersCollection)


def test_options_do_not_share_header_collections():
    """
    Two options built without explicit collections must not see each other's headers.
    """
    first = HeadersInspectionHandlerOption()
    second = HeadersInspectionHandlerOption()

    first.request_headers.add('test_request', 'test_request_header')
    first.response_headers.add('test_response', 'test_response_header')

    assert first.request_headers is not second.request_headers
    assert first.response_headers is not second.response_headers
    assert second.request_headers.try_get('test_request') is False
    assert second.response_headers.try_get('test_response') is False


def test_handlers_do_not_share_options():
    """
    Two handlers built without explicit options must not share one option object,
    or the headers one client inspects show up on, and get cleared by, another.
    """
    first = HeadersInspectionHandler()
    second = HeadersInspectionHandler()

    first.options.request_headers.add('test_request', 'test_request_header')

    assert first.options is not second.options
    assert second.options.request_headers.try_get('test_request') is False


def test_custom_config():
    """
    Ensures that setting is_enabled to False.
    """

    options = HeadersInspectionHandlerOption(inspect_request_headers=False)
    assert not options.inspect_request_headers


def test_headers_inspection_handler_construction():
    """
    Ensures the Header Inspection handler instance is set.
    """
    handler = HeadersInspectionHandler()
    assert handler


@pytest.mark.asyncio
async def test_headers_inspection_handler_gets_headers():

    def request_handler(request: httpx.Request):
        return httpx.Response(
            200, json={"text": "Hello, world!"}, headers={'test_response': 'test_response_header'}
        )

    handler = HeadersInspectionHandler()

    # First request
    request = httpx.Request(
        'GET', 'https://localhost', headers={'test_request': 'test_request_header'}
    )
    mock_transport = httpx.MockTransport(request_handler)
    resp = await handler.send(request, mock_transport)
    assert resp.status_code == 200
    assert handler.options.request_headers.try_get('test_request') == {'test_request_header'}
    assert handler.options.response_headers.try_get('test_response') == {'test_response_header'}

    # Second request
    request2 = httpx.Request(
        'GET', 'https://localhost', headers={'test_request_2': 'test_request_header_2'}
    )
    resp = await handler.send(request2, mock_transport)
    assert resp.status_code == 200
    assert not handler.options.request_headers.try_get('test_request') == {'test_request_header'}
    assert handler.options.request_headers.try_get('test_request_2') == {'test_request_header_2'}
    assert handler.options.response_headers.try_get('test_response') == {'test_response_header'}


@pytest.mark.asyncio
async def test_send_request_none_raises_type_error():
    handler = HeadersInspectionHandler()
    mock_transport = httpx.MockTransport(lambda req: httpx.Response(200))
    with pytest.raises(TypeError, match="request cannot be null"):
        await handler.send(None, mock_transport)


@pytest.mark.asyncio
async def test_headers_inspection_handler_request_options_isolation_and_clearing():

    def request_handler(request: httpx.Request):
        return httpx.Response(200, headers={"test_response": "resp_val_1"})

    handler = HeadersInspectionHandler()
    custom_options = HeadersInspectionHandlerOption()

    request1 = httpx.Request(
        "GET",
        "https://localhost",
        headers={"test_request": "req_val_1"},
        extensions={
            REQUEST_OPTIONS_KEY: {
                HeadersInspectionHandlerOption.get_key(): custom_options
            }
        },
    )
    mock_transport = httpx.MockTransport(request_handler)
    resp1 = await handler.send(request1, mock_transport)
    assert resp1.status_code == 200
    assert custom_options.request_headers.try_get("test_request") == {"req_val_1"}
    assert custom_options.response_headers.try_get("test_response") == {"resp_val_1"}

    # Second request reusing custom_options should clear previous request/response headers
    def request_handler_2(request: httpx.Request):
        return httpx.Response(200, headers={"test_response_2": "resp_val_2"})

    request2 = httpx.Request(
        "GET",
        "https://localhost",
        headers={"test_request_2": "req_val_2"},
        extensions={
            REQUEST_OPTIONS_KEY: {
                HeadersInspectionHandlerOption.get_key(): custom_options
            }
        },
    )
    mock_transport_2 = httpx.MockTransport(request_handler_2)
    resp2 = await handler.send(request2, mock_transport_2)
    assert resp2.status_code == 200
    assert custom_options.request_headers.try_get("test_request") is False
    assert custom_options.request_headers.try_get("test_request_2") == {"req_val_2"}
    assert custom_options.response_headers.try_get("test_response") is False
    assert custom_options.response_headers.try_get("test_response_2") == {"resp_val_2"}


@pytest.mark.asyncio
async def test_headers_inspection_handler_multi_valued_headers():

    def request_handler(request: httpx.Request):
        return httpx.Response(
            200,
            headers=[
                ("Set-Cookie", "session=abc; Path=/"),
                ("Set-Cookie", "theme=dark; Path=/"),
                ("X-Custom-List", "item1"),
                ("X-Custom-List", "item2"),
            ],
        )

    handler = HeadersInspectionHandler()
    request = httpx.Request(
        "GET",
        "https://localhost",
        headers=[
            ("Accept", "application/json"),
            ("Accept", "text/plain"),
        ],
    )
    mock_transport = httpx.MockTransport(request_handler)
    resp = await handler.send(request, mock_transport)
    assert resp.status_code == 200
    assert handler.options.request_headers.try_get("accept") == {"application/json", "text/plain"}
    assert handler.options.response_headers.try_get("set-cookie") == {
        "session=abc; Path=/",
        "theme=dark; Path=/",
    }
    assert handler.options.response_headers.try_get("x-custom-list") == {"item1", "item2"}


@pytest.mark.asyncio
async def test_span_ends_on_transport_failure(span_exporter):

    def request_handler(request):
        raise httpx.ReadError("request interrupted")

    handler = HeadersInspectionHandler()
    request = httpx.Request("GET", "https://localhost")
    async with httpx.MockTransport(request_handler) as transport:
        with pytest.raises(httpx.ReadError):
            await handler.send(request, transport)

    assert [span.name
            for span in span_exporter.get_finished_spans()] == ["HeadersInspectionHandler_send"]
