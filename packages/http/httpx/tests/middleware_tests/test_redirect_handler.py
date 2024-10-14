import httpx
import pytest

from kiota_http.middleware import RedirectHandler
from kiota_http.middleware.options import RedirectHandlerOption

BASE_URL = 'https://example.com'
REDIRECT_URL = "https://example.com/foo"
LOCATION_HEADER: str = "Location"
AUTHORIZATION_HEADER: str = "Authorization"
MOVED_PERMANENTLY = 301
FOUND = 302
SEE_OTHER = 303
TEMPORARY_REDIRECT = 307
PERMANENT_REDIRECT = 308


@pytest.fixture
def mock_redirect_handler():
    return RedirectHandler()


def test_no_config():
    """
    Test that default values are used if no custom confguration is passed
    """
    options = RedirectHandlerOption()
    handler = RedirectHandler()
    assert handler.options.should_redirect == options.should_redirect
    assert handler.options.max_redirect == options.max_redirect
    assert handler.redirect_on_status_codes == handler.DEFAULT_REDIRECT_STATUS_CODES


def test_custom_options():
    """
    Test that default configuration is overrriden if custom configuration is provided
    """
    options = RedirectHandlerOption()
    options.max_redirect = 3
    options.should_redirect = False

    handler = RedirectHandler(options)

    assert handler.options.max_redirect == 3
    assert not handler.options.should_redirect


def test_increment_redirects():
    """
    Tests that redirect are incremented
    """
    request = httpx.Request('GET', BASE_URL)
    response = httpx.Response(MOVED_PERMANENTLY, request=request)
    history = []

    handler = RedirectHandler()
    assert handler.increment(response, handler.options.max_redirect, history=history)


def test_same_origin(mock_redirect_handler):
    origin1 = httpx.URL(BASE_URL)
    origin2 = httpx.URL(f"{BASE_URL}:443")
    assert mock_redirect_handler._same_origin(origin1, origin2)


def test_not_same_origin(mock_redirect_handler):
    origin1 = httpx.URL(BASE_URL)
    origin2 = httpx.URL("HTTP://EXAMPLE.COM")
    assert not mock_redirect_handler._same_origin(origin1, origin2)


def test_is_https_redirect(mock_redirect_handler):
    url = httpx.URL("http://example.com")
    location = httpx.URL(BASE_URL)
    assert mock_redirect_handler.is_https_redirect(url, location)


def test_is_not_https_redirect(mock_redirect_handler):
    url = httpx.URL(BASE_URL)
    location = httpx.URL("http://www.example.com")
    assert not mock_redirect_handler.is_https_redirect(url, location)


@pytest.mark.asyncio
async def test_ok_response_not_redirected():
    """Test that a 200 response is not redirected"""

    def request_handler(request: httpx.Request):
        return httpx.Response(200, )

    handler = RedirectHandler()
    request = httpx.Request(
        'GET',
        BASE_URL,
    )
    mock_transport = httpx.MockTransport(request_handler)
    resp = await handler.send(request, mock_transport)
    assert resp.status_code == 200
    assert resp.request
    assert resp.request == request


@pytest.mark.asyncio
async def test_redirects_valid():
    """Test that a valid response is redirected"""

    def request_handler(request: httpx.Request):
        if request.url == REDIRECT_URL:
            return httpx.Response(200, )
        return httpx.Response(
            MOVED_PERMANENTLY,
            headers={LOCATION_HEADER: REDIRECT_URL},
        )

    handler = RedirectHandler()
    request = httpx.Request(
        'GET',
        BASE_URL,
    )
    mock_transport = httpx.MockTransport(request_handler)
    resp = await handler.send(request, mock_transport)
    assert resp.status_code == 200
    assert resp.request != request
    assert resp.request.method == request.method
    assert resp.request.url == REDIRECT_URL


@pytest.mark.asyncio
async def test_redirect_to_different_host_removes_auth_header():
    """Test that if a request is redirected to a different host,
    the Authorization header is removed"""

    def request_handler(request: httpx.Request):
        if request.url == "https://httpbin.org":
            return httpx.Response(200, )
        return httpx.Response(
            FOUND,
            headers={LOCATION_HEADER: "https://httpbin.org"},
        )

    handler = RedirectHandler()
    request = httpx.Request(
        'GET',
        BASE_URL,
        headers={AUTHORIZATION_HEADER: "Bearer token"},
    )
    mock_transport = httpx.MockTransport(request_handler)
    resp = await handler.send(request, mock_transport)
    assert resp.status_code == 200
    assert resp.request != request
    assert resp.request.method == request.method
    assert resp.request.url == "https://httpbin.org"
    assert AUTHORIZATION_HEADER not in resp.request.headers


@pytest.mark.asyncio
async def test_redirect_on_scheme_change_disabled():
    """Test that a request is not redirected if the scheme changes and
    allow_redirect_on_scheme_change is set to False"""

    def request_handler(request: httpx.Request):
        if request.url == "http://example.com":
            return httpx.Response(200, )
        return httpx.Response(
            TEMPORARY_REDIRECT,
            headers={LOCATION_HEADER: "http://example.com"},
        )

    handler = RedirectHandler()
    request = httpx.Request(
        'GET',
        BASE_URL,
    )
    mock_transport = httpx.MockTransport(request_handler)

    with pytest.raises(Exception):
        await handler.send(request, mock_transport)


@pytest.mark.asyncio
async def test_redirect_on_scheme_change_removes_auth_header():
    """Test that if a request is redirected to a different scheme,
    the Authorization header is removed"""

    def request_handler(request: httpx.Request):
        if request.url == "http://example.com":
            return httpx.Response(200, )
        return httpx.Response(
            TEMPORARY_REDIRECT,
            headers={LOCATION_HEADER: "http://example.com"},
        )

    handler = RedirectHandler(RedirectHandlerOption(allow_redirect_on_scheme_change=True))
    request = httpx.Request(
        'GET',
        BASE_URL,
        headers={AUTHORIZATION_HEADER: "Bearer token"},
    )
    mock_transport = httpx.MockTransport(request_handler)
    resp = await handler.send(request, mock_transport)
    assert resp.status_code == 200
    assert resp.request != request
    assert AUTHORIZATION_HEADER not in resp.request.headers


@pytest.mark.asyncio
async def test_redirect_with_same_host_keeps_auth_header():
    """Test that if a request is redirected to the same host,
    the Authorization header is kept"""

    def request_handler(request: httpx.Request):
        if request.url == f"{BASE_URL}/foo":
            return httpx.Response(200, )
        return httpx.Response(
            TEMPORARY_REDIRECT,
            headers={LOCATION_HEADER: f"{BASE_URL}/foo"},
        )

    handler = RedirectHandler(RedirectHandlerOption(allow_redirect_on_scheme_change=True))
    request = httpx.Request(
        'GET',
        BASE_URL,
        headers={AUTHORIZATION_HEADER: "Bearer token"},
    )
    mock_transport = httpx.MockTransport(request_handler)
    resp = await handler.send(request, mock_transport)
    assert resp.status_code == 200
    assert resp.request != request
    assert AUTHORIZATION_HEADER in resp.request.headers


@pytest.mark.asyncio
async def test_redirect_with_relative_url_keeps_host():
    """Test that if a request is redirected to a relative url,
    the host is kept"""

    def request_handler(request: httpx.Request):
        if request.url == f"{BASE_URL}/foo":
            return httpx.Response(200, )
        return httpx.Response(
            TEMPORARY_REDIRECT,
            headers={LOCATION_HEADER: "/foo"},
        )

    handler = RedirectHandler(RedirectHandlerOption(allow_redirect_on_scheme_change=True))
    request = httpx.Request(
        'GET',
        BASE_URL,
        headers={AUTHORIZATION_HEADER: "Bearer token"},
    )
    mock_transport = httpx.MockTransport(request_handler)
    resp = await handler.send(request, mock_transport)
    assert resp.status_code == 200
    assert resp.request != request
    assert AUTHORIZATION_HEADER in resp.request.headers
    assert resp.request.url == f"{BASE_URL}/foo"


@pytest.mark.asyncio
async def test_max_redirects_exceeded():
    """Test that if the maximum number of redirects is exceeded, an exception is raised"""

    def request_handler(request: httpx.Request):
        if request.url == f"{BASE_URL}/foo":
            return httpx.Response(
                TEMPORARY_REDIRECT,
                headers={LOCATION_HEADER: "/bar"},
            )
        return httpx.Response(
            TEMPORARY_REDIRECT,
            headers={LOCATION_HEADER: "/foo"},
        )

    handler = RedirectHandler(RedirectHandlerOption(allow_redirect_on_scheme_change=True))
    request = httpx.Request(
        'GET',
        f"{BASE_URL}/foo",
        headers={AUTHORIZATION_HEADER: "Bearer token"},
    )
    mock_transport = httpx.MockTransport(request_handler)
    with pytest.raises(Exception) as e:
        await handler.send(request, mock_transport)
    assert "Too many redirects" in str(e.value)
