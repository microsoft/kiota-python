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


@pytest.mark.asyncio
async def test_redirect_cross_host_removes_auth_and_cookie():
    """Test that cross-host redirects remove both Authorization and Cookie headers"""

    def request_handler(request: httpx.Request):
        if request.url == "https://other.example.com/api":
            return httpx.Response(200, )
        return httpx.Response(
            MOVED_PERMANENTLY,
            headers={LOCATION_HEADER: "https://other.example.com/api"},
        )

    handler = RedirectHandler()
    request = httpx.Request(
        'GET',
        BASE_URL,
        headers={
            AUTHORIZATION_HEADER: "Bearer token",
            "Cookie": "session=SECRET"
        },
    )
    mock_transport = httpx.MockTransport(request_handler)
    resp = await handler.send(request, mock_transport)
    assert resp.status_code == 200
    assert AUTHORIZATION_HEADER not in resp.request.headers
    assert "Cookie" not in resp.request.headers


@pytest.mark.asyncio
async def test_redirect_scheme_change_removes_auth_and_cookie():
    """Test that scheme changes remove both Authorization and Cookie headers"""

    def request_handler(request: httpx.Request):
        if request.url == "http://example.com/api":
            return httpx.Response(200, )
        return httpx.Response(
            MOVED_PERMANENTLY,
            headers={LOCATION_HEADER: "http://example.com/api"},
        )

    handler = RedirectHandler(RedirectHandlerOption(allow_redirect_on_scheme_change=True))
    request = httpx.Request(
        'GET',
        BASE_URL,
        headers={
            AUTHORIZATION_HEADER: "Bearer token",
            "Cookie": "session=SECRET"
        },
    )
    mock_transport = httpx.MockTransport(request_handler)
    resp = await handler.send(request, mock_transport)
    assert resp.status_code == 200
    assert AUTHORIZATION_HEADER not in resp.request.headers
    assert "Cookie" not in resp.request.headers


@pytest.mark.asyncio
async def test_redirect_same_host_and_scheme_keeps_all_headers():
    """Test that same-host and same-scheme redirects keep Authorization and Cookie headers"""

    def request_handler(request: httpx.Request):
        if request.url == f"{BASE_URL}/v2/api":
            return httpx.Response(200, )
        return httpx.Response(
            MOVED_PERMANENTLY,
            headers={LOCATION_HEADER: f"{BASE_URL}/v2/api"},
        )

    handler = RedirectHandler()
    request = httpx.Request(
        'GET',
        f"{BASE_URL}/v1/api",
        headers={
            AUTHORIZATION_HEADER: "Bearer token",
            "Cookie": "session=SECRET"
        },
    )
    mock_transport = httpx.MockTransport(request_handler)
    resp = await handler.send(request, mock_transport)
    assert resp.status_code == 200
    assert AUTHORIZATION_HEADER in resp.request.headers
    assert resp.request.headers[AUTHORIZATION_HEADER] == "Bearer token"
    assert "Cookie" in resp.request.headers
    assert resp.request.headers["Cookie"] == "session=SECRET"


@pytest.mark.asyncio
async def test_redirect_with_custom_scrubber():
    """Test that custom scrubber can be provided and is used"""

    def custom_scrubber(headers, original_url, new_url):
        # Custom logic: never remove headers
        pass

    def request_handler(request: httpx.Request):
        if request.url == "https://evil.attacker.com/steal":
            return httpx.Response(200, )
        return httpx.Response(
            MOVED_PERMANENTLY,
            headers={LOCATION_HEADER: "https://evil.attacker.com/steal"},
        )

    options = RedirectHandlerOption(scrub_sensitive_headers=custom_scrubber)
    handler = RedirectHandler(options)
    request = httpx.Request(
        'GET',
        BASE_URL,
        headers={
            AUTHORIZATION_HEADER: "Bearer token",
            "Cookie": "session=SECRET"
        },
    )
    mock_transport = httpx.MockTransport(request_handler)
    resp = await handler.send(request, mock_transport)
    assert resp.status_code == 200
    # Headers should be kept because custom scrubber doesn't remove them
    assert AUTHORIZATION_HEADER in resp.request.headers
    assert "Cookie" in resp.request.headers


def test_default_scrub_sensitive_headers_removes_on_host_change():
    """Test that default scrubber removes Authorization and Cookie when host changes"""
    from kiota_http.middleware.options.redirect_handler_option import default_scrub_sensitive_headers

    headers = httpx.Headers({
        AUTHORIZATION_HEADER: "Bearer token",
        "Cookie": "session=SECRET",
        "Content-Type": "application/json"
    })
    original_url = httpx.URL("https://example.com/v1/api")
    new_url = httpx.URL("https://other.com/api")

    default_scrub_sensitive_headers(headers, original_url, new_url)

    assert AUTHORIZATION_HEADER not in headers
    assert "Cookie" not in headers
    assert "Content-Type" in headers  # Other headers should remain


def test_default_scrub_sensitive_headers_removes_on_scheme_change():
    """Test that default scrubber removes Authorization and Cookie when scheme changes"""
    from kiota_http.middleware.options.redirect_handler_option import default_scrub_sensitive_headers

    headers = httpx.Headers({
        AUTHORIZATION_HEADER: "Bearer token",
        "Cookie": "session=SECRET",
        "Content-Type": "application/json"
    })
    original_url = httpx.URL("https://example.com/v1/api")
    new_url = httpx.URL("http://example.com/v1/api")

    default_scrub_sensitive_headers(headers, original_url, new_url)

    assert AUTHORIZATION_HEADER not in headers
    assert "Cookie" not in headers
    assert "Content-Type" in headers


def test_default_scrub_sensitive_headers_keeps_on_same_origin():
    """Test that default scrubber keeps headers when host and scheme are the same"""
    from kiota_http.middleware.options.redirect_handler_option import default_scrub_sensitive_headers

    headers = httpx.Headers({
        AUTHORIZATION_HEADER: "Bearer token",
        "Cookie": "session=SECRET",
        "Content-Type": "application/json"
    })
    original_url = httpx.URL("https://example.com/v1/api")
    new_url = httpx.URL("https://example.com/v2/api")

    default_scrub_sensitive_headers(headers, original_url, new_url)

    assert AUTHORIZATION_HEADER in headers
    assert "Cookie" in headers
    assert "Content-Type" in headers


def test_default_scrub_sensitive_headers_handles_none_gracefully():
    """Test that default scrubber handles None/empty inputs gracefully"""
    from kiota_http.middleware.options.redirect_handler_option import default_scrub_sensitive_headers

    # Should not raise exceptions
    default_scrub_sensitive_headers(None, httpx.URL(BASE_URL), httpx.URL(BASE_URL))
    default_scrub_sensitive_headers(httpx.Headers(), None, httpx.URL(BASE_URL))
    default_scrub_sensitive_headers(httpx.Headers(), httpx.URL(BASE_URL), None)


def test_custom_scrub_sensitive_headers():
    """Test that custom scrubber can be set on options"""
    def custom_scrubber(headers, original_url, new_url):
        # Custom logic
        pass

    options = RedirectHandlerOption(scrub_sensitive_headers=custom_scrubber)
    assert options.scrub_sensitive_headers == custom_scrubber


def test_default_options_uses_default_scrubber():
    """Test that default options use the default scrubber"""
    from kiota_http.middleware.options.redirect_handler_option import default_scrub_sensitive_headers

    options = RedirectHandlerOption()
    assert options.scrub_sensitive_headers == default_scrub_sensitive_headers
