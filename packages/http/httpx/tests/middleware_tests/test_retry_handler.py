from email.utils import formatdate
from time import time

import httpx
import pytest

from kiota_http.middleware import RetryHandler
from kiota_http.middleware.options import RetryHandlerOption

BASE_URL = 'https://httpbin.org'
RETRY_AFTER = "Retry-After"
RETRY_ATTEMPT = "Retry-Attempt"
GATEWAY_TIMEOUT = 504
SERVICE_UNAVAILABLE = 503
TOO_MANY_REQUESTS = 429


def test_no_config():
    """
    Test that default values are used if no custom confguration is passed
    """
    options = RetryHandlerOption()
    retry_handler = RetryHandler()
    assert retry_handler.options.max_retry == options.max_retry
    assert retry_handler.options.max_delay == options.max_delay
    assert retry_handler.allowed_methods == frozenset(
        ['HEAD', 'GET', 'PUT', 'POST', 'PATCH', 'DELETE', 'OPTIONS']
    )
    assert retry_handler.respect_retry_after_header


def test_custom_options():
    """
    Test that default configuration is overrriden if custom configuration is provided
    """
    options = RetryHandlerOption(100, 1, False)
    retry_handler = RetryHandler(options)

    assert retry_handler.options.max_retry == 1
    assert retry_handler.options.max_delay == 100
    assert not retry_handler.options.should_retry


def test_method_retryable_with_valid_method():
    """
    Test if method is retryable with a retryable request method.
    """
    request = httpx.Request('GET', BASE_URL)
    retry_handler = RetryHandler()
    assert retry_handler._is_method_retryable(request)


def test_should_retry_valid():
    """
    Test the should_retry method with a valid HTTP method and response code
    """
    request = httpx.Request('GET', BASE_URL)
    response = httpx.Response(SERVICE_UNAVAILABLE)

    retry_handler = RetryHandler()
    assert retry_handler.should_retry(
        request,
        retry_handler.options,
        response,
    )


def test_should_retry_invalid():
    """
    Test the should_retry method with an invalid HTTP response code
    """
    request = httpx.Request('GET', BASE_URL)
    response = httpx.Response(502)

    retry_handler = RetryHandler()

    assert not retry_handler.should_retry(request, retry_handler.options, response)


def test_is_request_payload_buffered_valid():
    """
    Test for _is_request_payload_buffered helper method.
    Should return true request payload is buffered/rewindable.
    """
    request = httpx.Request('GET', BASE_URL)

    retry_handler = RetryHandler()

    assert retry_handler._is_request_payload_buffered(request)


def test_is_request_payload_buffered_invalid():
    """
    Test for _is_request_payload_buffered helper method.
    Should return false if request payload is forward streamed.
    """
    request = httpx.Request('POST', BASE_URL, headers={'Content-Type': "application/octet-stream"})

    retry_handler = RetryHandler()

    assert not retry_handler._is_request_payload_buffered(request)


def test_check_retry_valid():
    """
    Test that a retry is valid if the maximum number of retries has not been reached
    """
    retry_handler = RetryHandler()

    assert retry_handler.check_retry_valid(0, retry_handler.options)


def test_check_retry_valid_no_retries():
    """
    Test that a retry is not valid if maximum number of retries has been reached
    """
    options = RetryHandlerOption()
    options.max_retry = 2
    retry_handler = RetryHandler(options)

    assert not retry_handler.check_retry_valid(2, retry_handler.options)


def test_get_retry_after():
    """
    Test the _get_retry_after method with an integer value for retry header.
    """
    response = httpx.Response(SERVICE_UNAVAILABLE, headers={RETRY_AFTER: "120"})
    retry_handler = RetryHandler()

    assert retry_handler._get_retry_after(response) == 120


def test_get_retry_after_no_header():
    """
    Test the _get_retry_after method with no Retry-After header.
    """
    response = httpx.Response(SERVICE_UNAVAILABLE)

    retry_handler = RetryHandler()

    assert retry_handler._get_retry_after(response) is None


def test_get_retry_after_http_date():
    """
    Test the _get_retry_after method with a http date as Retry-After value.
    """
    timevalue = time() + 120
    http_date = formatdate(timeval=timevalue, localtime=False, usegmt=True)
    response = httpx.Response(SERVICE_UNAVAILABLE, headers={RETRY_AFTER: f'{http_date}'})

    retry_handler = RetryHandler()
    assert retry_handler._get_retry_after(response) < 120


@pytest.mark.asyncio
async def test_ok_response_not_retried():
    """Test that a 200 response is not retried"""

    def request_handler(request: httpx.Request):
        return httpx.Response(200, )

    handler = RetryHandler()
    request = httpx.Request(
        'GET',
        BASE_URL,
    )
    mock_transport = httpx.MockTransport(request_handler)
    resp = await handler.send(request, mock_transport)
    assert resp.status_code == 200
    assert resp.request
    assert resp.request == request
    assert RETRY_ATTEMPT not in resp.request.headers


@pytest.mark.asyncio
async def test_retries_valid():
    """Test that a valid response is retried"""

    def request_handler(request: httpx.Request):
        if RETRY_ATTEMPT in request.headers:
            return httpx.Response(200, )
        return httpx.Response(SERVICE_UNAVAILABLE, )

    handler = RetryHandler()
    request = httpx.Request(
        'GET',
        BASE_URL,
    )
    mock_transport = httpx.MockTransport(request_handler)
    resp = await handler.send(request, mock_transport)
    assert resp.status_code == 200
    assert RETRY_ATTEMPT in resp.request.headers
    assert resp.request.headers[RETRY_ATTEMPT] == '1'


@pytest.mark.asyncio
async def test_should_retry_false():
    """Test that a request is not retried if should_retry is set to False"""

    def request_handler(request: httpx.Request):
        if RETRY_ATTEMPT in request.headers:
            return httpx.Response(200, )
        return httpx.Response(TOO_MANY_REQUESTS, )

    handler = RetryHandler(RetryHandlerOption(10, 1, False))
    request = httpx.Request(
        'GET',
        BASE_URL,
    )
    mock_transport = httpx.MockTransport(request_handler)
    resp = await handler.send(request, mock_transport)
    assert resp.status_code == TOO_MANY_REQUESTS
    assert RETRY_ATTEMPT not in resp.request.headers


@pytest.mark.asyncio
async def test_returns_same_status_code_if_delay_greater_than_max_delay():
    """Test that a request is delayed based on the Retry-After header"""

    def request_handler(request: httpx.Request):
        if RETRY_ATTEMPT in request.headers:
            return httpx.Response(200, )
        return httpx.Response(
            TOO_MANY_REQUESTS,
            headers={RETRY_AFTER: "20"},
        )

    handler = RetryHandler(RetryHandlerOption(10, 1, True))
    request = httpx.Request(
        'GET',
        BASE_URL,
    )
    mock_transport = httpx.MockTransport(request_handler)
    resp = await handler.send(request, mock_transport)
    assert resp.status_code == 429
    assert RETRY_ATTEMPT not in resp.request.headers


@pytest.mark.asyncio
async def test_retry_options_apply_per_request():
    """Test that a request options are applied per request"""

    def request_handler(request: httpx.Request):
        if "request_1" in request.headers:
            return httpx.Response(SERVICE_UNAVAILABLE, )
        return httpx.Response(GATEWAY_TIMEOUT, )

    handler = RetryHandler(RetryHandlerOption(10, 2, True))

    # Requet 1
    request = httpx.Request('GET', BASE_URL, headers={"request_1": "request_1_header"})
    mock_transport = httpx.MockTransport(request_handler)
    resp = await handler.send(request, mock_transport)
    assert resp.status_code == SERVICE_UNAVAILABLE
    assert 'request_1' in resp.request.headers
    assert resp.request.headers[RETRY_ATTEMPT] == '2'

    # Request 2
    request = httpx.Request('GET', BASE_URL, headers={"request_2": "request_2_header"})
    mock_transport = httpx.MockTransport(request_handler)
    resp = await handler.send(request, mock_transport)
    assert resp.status_code == GATEWAY_TIMEOUT
    assert 'request_2' in resp.request.headers
    assert resp.request.headers[RETRY_ATTEMPT] == '2'
