import pytest
import httpx

from unittest.mock import AsyncMock

from kiota_abstractions.headers_collection import HeadersCollection
from kiota_http.middleware.middleware import BaseMiddleware
from kiota_http.middleware.options.headers_inspection_handler_option import HeadersInspectionHandlerOption
from kiota_http.middleware.headers_inspection_handler import HeadersInspectionHandler


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
