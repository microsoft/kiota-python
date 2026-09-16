import asyncio

import httpx
import pytest

from kiota_http._exceptions import RedirectError
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


@pytest.mark.asyncio
@pytest.mark.parametrize("redirects, should_redirect", [(0, True), (2, True), (1, False)])
async def test_redirect_spans_end(redirects, should_redirect, span_exporter):
    requests = []

    def request_handler(request):
        requests.append(request)
        if len(requests) <= redirects:
            return httpx.Response(302, headers={LOCATION_HEADER: f"/redirect/{len(requests)}"})
        return httpx.Response(200)

    options = RedirectHandlerOption()
    options.should_redirect = should_redirect
    async with httpx.MockTransport(request_handler) as transport:
        response = await RedirectHandler(options).send(httpx.Request("GET", BASE_URL), transport)

    attempts = redirects + 1 if should_redirect else 1
    assert len(requests) == attempts
    assert response.status_code == (200 if should_redirect else 302)
    assert len(response.history) == attempts - 1
    spans = span_exporter.get_finished_spans()
    assert [span.name for span in spans] == ["RedirectHandler_send"] + [
        f"RedirectHandler_send - redirect {index}" for index in range(attempts)
    ]
    assert spans[-1].attributes["http.response.status_code"] == response.status_code


@pytest.mark.asyncio
async def test_redirect_limit_span_records_error_before_ending(span_exporter):
    options = RedirectHandlerOption()
    options.max_redirect = 1
    transport = httpx.MockTransport(
        lambda request: httpx.Response(302, headers={LOCATION_HEADER: "/next"})
    )
    async with transport:
        with pytest.raises(RedirectError, match="Too many redirects") as error:
            await RedirectHandler(options).send(httpx.Request("GET", BASE_URL), transport)

    spans = span_exporter.get_finished_spans()
    assert [span.name for span in spans] == [
        "RedirectHandler_send", "RedirectHandler_send - redirect 0",
        "RedirectHandler_send - redirect 1"
    ]
    assert spans[-1].events[0].name == "exception"
    assert spans[-1].events[0].attributes["exception.message"] == str(error.value)


@pytest.mark.asyncio
@pytest.mark.parametrize("error_type", [httpx.ReadError, asyncio.CancelledError])
async def test_redirect_span_ends_on_transport_failure(error_type, span_exporter):
    error = error_type("request interrupted")

    def request_handler(request):
        raise error

    async with httpx.MockTransport(request_handler) as transport:
        with pytest.raises(error_type) as raised:
            await RedirectHandler().send(httpx.Request("GET", BASE_URL), transport)
    assert raised.value is error
    assert [span.name for span in span_exporter.get_finished_spans()] == [
        "RedirectHandler_send", "RedirectHandler_send - redirect 0"
    ]


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
        if request.url == "http://example.com/api":  # NOSONAR
            return httpx.Response(200, )
        return httpx.Response(
            MOVED_PERMANENTLY,
            headers={LOCATION_HEADER: "http://example.com/api"},  # NOSONAR
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
async def test_redirect_with_different_port_removes_auth_and_cookie():
    """Test that redirects to a different port remove Authorization and Cookie headers"""

    def request_handler(request: httpx.Request):
        if request.url == "http://example.org:9090/bar":  # NOSONAR
            return httpx.Response(200, )
        return httpx.Response(
            MOVED_PERMANENTLY,
            headers={LOCATION_HEADER: "http://example.org:9090/bar"},  # NOSONAR
        )

    handler = RedirectHandler()
    request = httpx.Request(
        'GET',
        "http://example.org:8080/foo",  # NOSONAR
        headers={
            AUTHORIZATION_HEADER: "Bearer token",
            "Cookie": "session=SECRET"
        },
    )
    mock_transport = httpx.MockTransport(request_handler)
    resp = await handler.send(request, mock_transport)
    assert resp.status_code == 200
    assert resp.request != request
    assert AUTHORIZATION_HEADER not in resp.request.headers
    assert "Cookie" not in resp.request.headers


@pytest.mark.asyncio
async def test_redirect_with_same_port_keeps_auth_and_cookie():
    """Test that redirects to the same port keep Authorization and Cookie headers"""

    def request_handler(request: httpx.Request):
        if request.url == "http://example.org:8080/bar":  # NOSONAR
            return httpx.Response(200, )
        return httpx.Response(
            FOUND,
            headers={LOCATION_HEADER: "http://example.org:8080/bar"},  # NOSONAR
        )

    handler = RedirectHandler()
    request = httpx.Request(
        'GET',
        "http://example.org:8080/foo",  # NOSONAR
        headers={
            AUTHORIZATION_HEADER: "Bearer token",
            "Cookie": "session=SECRET"
        },
    )
    mock_transport = httpx.MockTransport(request_handler)
    resp = await handler.send(request, mock_transport)
    assert resp.status_code == 200
    assert resp.request != request
    assert AUTHORIZATION_HEADER in resp.request.headers
    assert resp.request.headers[AUTHORIZATION_HEADER] == "Bearer token"
    assert "Cookie" in resp.request.headers
    assert resp.request.headers["Cookie"] == "session=SECRET"


@pytest.mark.asyncio
async def test_redirect_with_custom_scrubber():
    """Test that custom scrubber can be provided and is used"""

    def custom_scrubber(new_request, original_url):
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

    original_url = httpx.URL("https://example.com/v1/api")
    new_request = httpx.Request(
        "GET",
        "https://other.com/api",
        headers={
            AUTHORIZATION_HEADER: "Bearer token",
            "Cookie": "session=SECRET",
            "Content-Type": "application/json"
        }
    )

    default_scrub_sensitive_headers(new_request, original_url)

    assert AUTHORIZATION_HEADER not in new_request.headers
    assert "Cookie" not in new_request.headers
    assert "Content-Type" in new_request.headers  # Other headers should remain


def test_default_scrub_sensitive_headers_removes_on_scheme_change():
    """Test that default scrubber removes Authorization and Cookie when scheme changes"""
    from kiota_http.middleware.options.redirect_handler_option import default_scrub_sensitive_headers

    original_url = httpx.URL("https://example.com/v1/api")
    new_request = httpx.Request(
        "GET",
        "http://example.com/v1/api",  # NOSONAR
        headers={
            AUTHORIZATION_HEADER: "Bearer token",
            "Cookie": "session=SECRET",
            "Content-Type": "application/json"
        }
    )

    default_scrub_sensitive_headers(new_request, original_url)

    assert AUTHORIZATION_HEADER not in new_request.headers
    assert "Cookie" not in new_request.headers
    assert "Content-Type" in new_request.headers


def test_default_scrub_sensitive_headers_keeps_on_same_origin():
    """Test that default scrubber keeps headers when host and scheme are the same"""
    from kiota_http.middleware.options.redirect_handler_option import default_scrub_sensitive_headers

    original_url = httpx.URL("https://example.com/v1/api")
    new_request = httpx.Request(
        "GET",
        "https://example.com/v2/api",
        headers={
            AUTHORIZATION_HEADER: "Bearer token",
            "Cookie": "session=SECRET",
            "Content-Type": "application/json"
        }
    )

    default_scrub_sensitive_headers(new_request, original_url)

    assert AUTHORIZATION_HEADER in new_request.headers
    assert "Cookie" in new_request.headers
    assert "Content-Type" in new_request.headers


def test_default_scrub_sensitive_headers_removes_on_port_change():
    """Test that default scrubber removes Authorization and Cookie when port changes"""
    from kiota_http.middleware.options.redirect_handler_option import default_scrub_sensitive_headers

    original_url = httpx.URL("http://example.org:8080/foo")  # NOSONAR
    new_request = httpx.Request(
        "GET",
        "http://example.org:9090/bar",  # NOSONAR
        headers={
            AUTHORIZATION_HEADER: "Bearer token",
            "Cookie": "session=SECRET",
            "Content-Type": "application/json"
        }
    )

    default_scrub_sensitive_headers(new_request, original_url)

    assert AUTHORIZATION_HEADER not in new_request.headers
    assert "Cookie" not in new_request.headers
    assert "Content-Type" in new_request.headers  # Other headers should remain


def test_default_scrub_sensitive_headers_keeps_on_same_port():
    """Test that default scrubber keeps headers when port is the same"""
    from kiota_http.middleware.options.redirect_handler_option import default_scrub_sensitive_headers

    original_url = httpx.URL("http://example.org:8080/foo")  # NOSONAR
    new_request = httpx.Request(
        "GET",
        "http://example.org:8080/bar",  # NOSONAR
        headers={
            AUTHORIZATION_HEADER: "Bearer token",
            "Cookie": "session=SECRET",
            "Content-Type": "application/json"
        }
    )

    default_scrub_sensitive_headers(new_request, original_url)

    assert AUTHORIZATION_HEADER in new_request.headers
    assert "Cookie" in new_request.headers
    assert "Content-Type" in new_request.headers


def test_default_scrub_sensitive_headers_handles_none_gracefully():
    """Test that default scrubber handles None/empty inputs gracefully"""
    from kiota_http.middleware.options.redirect_handler_option import default_scrub_sensitive_headers

    # Should not raise exceptions
    default_scrub_sensitive_headers(None, httpx.URL(BASE_URL))
    default_scrub_sensitive_headers(httpx.Request("GET", BASE_URL), None)


def test_custom_scrub_sensitive_headers():
    """Test that custom scrubber can be set on options"""
    def custom_scrubber(new_request, original_url):
        # Custom logic
        pass

    options = RedirectHandlerOption(scrub_sensitive_headers=custom_scrubber)
    assert options.scrub_sensitive_headers == custom_scrubber


def test_default_options_uses_default_scrubber():
    """Test that default options use the default scrubber"""
    from kiota_http.middleware.options.redirect_handler_option import default_scrub_sensitive_headers

    options = RedirectHandlerOption()
    assert options.scrub_sensitive_headers == default_scrub_sensitive_headers
