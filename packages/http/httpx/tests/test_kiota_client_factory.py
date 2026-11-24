import asyncio
import gzip

import httpx
import pytest
from kiota_http.kiota_client_factory import KiotaClientFactory
from kiota_http.middleware import (
    REQUEST_OPTIONS_KEY,
    AsyncKiotaTransport,
    BodyInspectionHandler,
    CompressionHandler,
    HeadersInspectionHandler,
    MiddlewarePipeline,
    ParametersNameDecodingHandler,
    RedirectHandler,
    RetryHandler,
    UrlReplaceHandler,
)
from kiota_http.middleware.options import (
    BodyInspectionHandlerOption,
    HeadersInspectionHandlerOption,
    RedirectHandlerOption,
    RetryHandlerOption,
    UrlReplaceHandlerOption,
)
from kiota_http.middleware.retry_handler import RETRY_ATTEMPT
from kiota_http.middleware.user_agent_handler import UserAgentHandler


def test_create_with_default_middleware():
    """Test creation of HTTP Client using default middleware"""
    client = KiotaClientFactory.create_with_default_middleware()

    assert isinstance(client, httpx.AsyncClient)
    assert isinstance(client._transport, AsyncKiotaTransport)


def test_create_with_default_middleware_custom_client():
    """Test creation of HTTP Client using default middleware while providing
    a custom client"""
    timeout = httpx.Timeout(20, connect=10)
    custom_client = httpx.AsyncClient(timeout=timeout, http2=True)
    client = KiotaClientFactory.create_with_default_middleware(custom_client)

    assert isinstance(client, httpx.AsyncClient)
    assert client.timeout == httpx.Timeout(connect=10, read=20, write=20, pool=20)
    assert isinstance(client._transport, AsyncKiotaTransport)


def test_create_with_default_middleware_custom_client_with_proxy():
    """Test creation of HTTP Client using default middleware while providing
    a custom client"""
    proxies = {
        "http://": httpx.HTTPTransport(proxy="http://localhost:8030"),
        "https://": httpx.HTTPTransport(proxy="http://localhost:8031"),
    }
    timeout = httpx.Timeout(20, connect=10)
    custom_client = httpx.AsyncClient(timeout=timeout, http2=True, mounts=proxies, trust_env=False)
    client = KiotaClientFactory.create_with_default_middleware(custom_client)

    assert isinstance(client, httpx.AsyncClient)
    assert client.timeout == httpx.Timeout(connect=10, read=20, write=20, pool=20)
    assert isinstance(client._transport, AsyncKiotaTransport)
    assert client._mounts
    for pattern, transport in client._mounts.items():
        assert isinstance(transport, AsyncKiotaTransport)


def test_create_with_default_middleware_options():
    """Test creation of HTTP Client using default middleware and custom options"""
    retry_options = RetryHandlerOption(max_retries=5)
    options = {f'{retry_options.get_key()}': retry_options}
    client = KiotaClientFactory.create_with_default_middleware(options=options)

    assert isinstance(client, httpx.AsyncClient)
    assert isinstance(client._transport, AsyncKiotaTransport)
    pipeline = client._transport.pipeline
    redirect_handler = pipeline._first_middleware.next.next.next
    assert isinstance(redirect_handler, RedirectHandler)
    retry_handler = redirect_handler.next
    assert isinstance(retry_handler, RetryHandler)
    assert retry_handler.options.max_retry == retry_options.max_retry


def test_create_with_custom_middleware():
    """Test creation of HTTP Clients with custom middleware"""
    middleware = [
        RetryHandler(),
    ]
    client = KiotaClientFactory.create_with_custom_middleware(middleware=middleware)

    assert isinstance(client, httpx.AsyncClient)
    assert isinstance(client._transport, AsyncKiotaTransport)
    pipeline = client._transport.pipeline
    assert isinstance(pipeline._first_middleware, RetryHandler)


def test_create_with_custom_middleware_custom_client():
    """Test creation of HTTP Client using custom middleware while providing
    a custom client"""
    timeout = httpx.Timeout(20, connect=10)
    custom_client = httpx.AsyncClient(timeout=timeout, http2=True)
    middleware = [
        RetryHandler(),
    ]
    client = KiotaClientFactory.create_with_custom_middleware(middleware, custom_client)
    assert client.timeout == httpx.Timeout(connect=10, read=20, write=20, pool=20)
    assert isinstance(client._transport, AsyncKiotaTransport)
    pipeline = client._transport.pipeline
    assert isinstance(pipeline._first_middleware, RetryHandler)


def test_create_with_custom_middleware_custom_client_with_proxy():
    """Test creation of HTTP Client using custom middleware while providing
    a custom client"""
    proxies = {
        "http://": httpx.HTTPTransport(proxy="http://localhost:8030"),
        "https://": httpx.HTTPTransport(proxy="http://localhost:8031"),
    }
    timeout = httpx.Timeout(20, connect=10)
    custom_client = httpx.AsyncClient(timeout=timeout, http2=True, mounts=proxies, trust_env=False)
    middleware = [
        RetryHandler(),
    ]
    client = KiotaClientFactory.create_with_custom_middleware(middleware, custom_client)
    assert client.timeout == httpx.Timeout(connect=10, read=20, write=20, pool=20)
    assert isinstance(client._transport, AsyncKiotaTransport)
    pipeline = client._transport.pipeline
    assert isinstance(pipeline._first_middleware, RetryHandler)
    assert client._mounts
    for pattern, transport in client._mounts.items():
        assert isinstance(transport, AsyncKiotaTransport)
        pipeline = transport.pipeline
        assert isinstance(pipeline._first_middleware, RetryHandler)


def test_get_default_middleware():
    """Test fetching of default middleware with no custom options passed"""
    middleware = KiotaClientFactory.get_default_middleware(None)

    assert [type(handler) for handler in middleware] == [
        UrlReplaceHandler,
        ParametersNameDecodingHandler,
        UserAgentHandler,
        RedirectHandler,
        RetryHandler,
        HeadersInspectionHandler,
        BodyInspectionHandler,
    ]


def test_default_middleware_does_not_share_options():
    first = KiotaClientFactory.get_default_middleware(None)
    second = KiotaClientFactory.get_default_middleware(None)

    for first_handler, second_handler in zip(first, second):
        assert first_handler.options is not second_handler.options


def test_get_default_middleware_with_options():
    """Test fetching of default middleware with custom options passed"""
    retry_options = RetryHandlerOption(max_retries=7)
    redirect_options = RedirectHandlerOption(should_redirect=False)
    body_inspection_options = BodyInspectionHandlerOption(inspect_request_body=True)
    options = {
        f'{retry_options.get_key()}': retry_options,
        f'{redirect_options.get_key()}': redirect_options,
        f'{body_inspection_options.get_key()}': body_inspection_options,
    }

    middleware = KiotaClientFactory.get_default_middleware(options=options)

    assert len(middleware) == 7
    assert isinstance(middleware[3], RedirectHandler)
    assert middleware[3].options.should_redirect is False
    assert isinstance(middleware[4], RetryHandler)
    assert middleware[4].options.max_retry == 7
    assert isinstance(middleware[6], BodyInspectionHandler)
    assert middleware[6].options.inspect_request_body is True


@pytest.mark.asyncio
@pytest.mark.parametrize("redirect_status", [303, 307])
async def test_transforms_run_once_and_inspection_runs_per_attempt(redirect_status, mocker):
    initial_url = "https://example.com/start?plain=1"
    transformed_url = "https://example.com/start?$filter=1"
    redirect_url = "https://example.com/destination?%24filter=2"
    retry_handler = RetryHandler(RetryHandlerOption(max_retries=1))
    retry_handler.backoff_max = 0
    header_inspection = HeadersInspectionHandlerOption()
    body_inspection = BodyInspectionHandlerOption(inspect_request_body=True)
    replace_option = UrlReplaceHandlerOption(
        replacement_pairs={
            "plain": "%24filter",
            "destination": "rewritten"
        }
    )
    request_options = {
        option.get_key(): option
        for option in (header_inspection, body_inspection, replace_option)
    }
    middleware = KiotaClientFactory.get_default_middleware(None)
    user_agent_send = mocker.spy(middleware[2], "send")
    retry_index = next(
        i for i, handler in enumerate(middleware) if isinstance(handler, RetryHandler)
    )
    middleware[retry_index] = retry_handler
    middleware.insert(retry_index - 1, CompressionHandler())
    compress = mocker.spy(gzip, "compress")
    attempts = []

    def respond(request):
        assert REQUEST_OPTIONS_KEY not in request.extensions
        assert header_inspection.request_headers.contains("user-agent")
        is_retry = RETRY_ATTEMPT in request.headers
        assert header_inspection.request_headers.contains(RETRY_ATTEMPT) == is_retry
        assert body_inspection.request_body == (request.content or None)
        attempts.append((str(request.url), request.method, request.headers.copy(), request.content))
        if len(attempts) in (1, 3):
            return httpx.Response(503)
        if len(attempts) == 2:
            return httpx.Response(redirect_status, headers={"Location": redirect_url})
        return httpx.Response(200)

    async with KiotaClientFactory.create_with_custom_middleware(
        middleware, httpx.AsyncClient(transport=httpx.MockTransport(respond))
    ) as client:
        response = await client.post(
            initial_url,
            content=b"request body",
            headers={"Content-Type": "text/plain"},
            extensions={REQUEST_OPTIONS_KEY: request_options},
        )

    assert response.status_code == 200
    assert [url for url, _, _, _ in attempts] == [transformed_url] * 2 + [redirect_url] * 2
    assert [headers.get(RETRY_ATTEMPT) for _, _, headers, _ in attempts] == [None, "1", None, "1"]
    user_agent_send.assert_awaited_once()
    compress.assert_called_once_with(b"request body")
    encoded_body = attempts[0][3]
    assert gzip.decompress(encoded_body) == b"request body"
    for _, method, headers, body in attempts[:2] if redirect_status == 303 else attempts:
        assert method == "POST"
        assert headers["Content-Encoding"] == "gzip"
        assert headers["Content-Length"] == str(len(encoded_body))
        assert body == encoded_body
    if redirect_status == 303:
        for _, method, headers, body in attempts[2:]:
            assert method == "GET"
            assert "Content-Encoding" not in headers
            assert "Content-Length" not in headers
            assert "Content-Type" not in headers
            assert not body


@pytest.mark.asyncio
@pytest.mark.parametrize("redirect_status", [303, 307])
async def test_compression_fallback_is_scoped_to_the_rejected_hop(redirect_status, mocker):
    source_url = "https://example.com/start"
    target_url = "https://other.example.com/target"
    payload = b"request body"
    body_inspection = BodyInspectionHandlerOption(inspect_request_body=True)
    retry = RetryHandler(RetryHandlerOption(max_retries=0))
    retry.backoff_max = 0
    retry_option = RetryHandlerOption(max_retries=1)
    options = {option.get_key(): option for option in (retry_option, body_inspection)}
    compress = mocker.spy(gzip, "compress")
    attempts = []
    context = object()

    def respond(request):
        assert REQUEST_OPTIONS_KEY not in request.extensions
        assert request.extensions["custom"] == "metadata"
        assert request.context is context
        assert body_inspection.request_body == (request.content or None)
        attempts.append((str(request.url), request.method, request.headers.copy(), request.content))
        if str(request.url) == source_url:
            assert len(attempts) == 1
            return httpx.Response(redirect_status, headers={"Location": target_url})
        assert str(request.url) == target_url
        assert request.headers["Host"] == "other.example.com"
        assert "Authorization" not in request.headers
        assert "Cookie" not in request.headers
        assert request.headers["X-Custom"] == "kept"
        if len(attempts) == 2:
            return httpx.Response(415)
        if len(attempts) == 3:
            return httpx.Response(503)
        return httpx.Response(200)

    middleware = [CompressionHandler(), RedirectHandler(), retry, BodyInspectionHandler()]
    async with KiotaClientFactory.create_with_custom_middleware(
        middleware, httpx.AsyncClient(transport=httpx.MockTransport(respond))
    ) as client:
        request = client.build_request(
            "POST",
            source_url,
            content=payload,
            headers={
                "Authorization": "Bearer example",
                "Cookie": "example=value",
                "Content-Type": "text/plain",
                "X-Custom": "kept",
            },
            extensions={
                REQUEST_OPTIONS_KEY: options,
                "custom": "metadata"
            },
        )
        request.context = context
        response = await client.send(request)

    compress.assert_called_once_with(payload)
    assert gzip.decompress(attempts[0][3]) == payload
    _, method, headers, body = attempts[1]
    if redirect_status == 303:
        assert response.status_code == 415
        assert len(attempts) == 2
        assert method == "GET" and not body
        assert "Content-Encoding" not in headers
    else:
        assert response.status_code == 200
        assert len(attempts) == 4
        assert method == "POST" and body == attempts[0][3]
        assert headers["Content-Encoding"] == "gzip"
        for _, method, headers, body in attempts[2:]:
            assert method == "POST" and body == payload
            assert "Content-Encoding" not in headers
            assert headers["Content-Type"] == "text/plain"
            assert headers["Content-Length"] == str(len(payload))
        assert [headers.get(RETRY_ATTEMPT)
                for _, _, headers, _ in attempts] == [None, None, None, "1"]


@pytest.mark.asyncio
async def test_retry_before_redirect_stops_at_max_retries():
    retry = RetryHandler(RetryHandlerOption(max_retries=1))
    retry.backoff_max = 0
    attempts = []

    def respond(request):
        attempts.append((request.url.path, request.headers.get(RETRY_ATTEMPT)))
        assert len(attempts) <= 4, "retry budget exceeded"
        if request.url.path == "/start":
            return httpx.Response(307, headers={"Location": "/target"})
        return httpx.Response(503)

    async with KiotaClientFactory.create_with_custom_middleware(
        [retry, RedirectHandler()], httpx.AsyncClient(transport=httpx.MockTransport(respond))
    ) as client:
        response = await client.get("https://example.com/start")

    assert response.status_code == 503
    assert attempts == [("/start", None), ("/target", None), ("/start", "1"), ("/target", None)]


def test_create_middleware_pipeline():

    middleware = KiotaClientFactory.get_default_middleware(None)
    pipeline = KiotaClientFactory.create_middleware_pipeline(
        middleware,
        httpx.AsyncClient()._transport
    )

    assert isinstance(pipeline, MiddlewarePipeline)


class ClosingTransport(httpx.MockTransport):

    def __init__(self, handler):
        super().__init__(handler)
        self.close_count = 0

    async def aclose(self):
        self.close_count += 1
        await super().aclose()


@pytest.mark.asyncio
@pytest.mark.parametrize('use_context_manager', [False, True])
async def test_client_closes_wrapped_transports(use_context_manager):
    transport = ClosingTransport(lambda request: httpx.Response(200))
    mounted_transport = ClosingTransport(lambda request: httpx.Response(200))
    client = KiotaClientFactory.create_with_default_middleware(
        httpx.AsyncClient(
            transport=transport,
            mounts={'https://mounted.example.com': mounted_transport},
            trust_env=False
        )
    )

    async def send_requests():
        assert (await client.get('https://example.com')).status_code == 200
        assert (await client.get('https://mounted.example.com')).status_code == 200
        assert transport.close_count == 0
        assert mounted_transport.close_count == 0

    if use_context_manager:
        async with client:
            await send_requests()
    else:
        await send_requests()
        await client.aclose()

    assert client.is_closed
    assert transport.close_count == 1
    assert mounted_transport.close_count == 1
    await client.aclose()
    assert transport.close_count == 1
    assert mounted_transport.close_count == 1


@pytest.mark.asyncio
@pytest.mark.parametrize('error_type', [RuntimeError, asyncio.CancelledError])
async def test_client_closes_wrapped_transport_after_request_failure(error_type):
    def fail_request(request):
        raise error_type('request interrupted')

    transport = ClosingTransport(fail_request)
    client = KiotaClientFactory.create_with_default_middleware(
        httpx.AsyncClient(transport=transport, trust_env=False)
    )

    with pytest.raises(error_type, match='request interrupted'):
        async with client:
            await client.get('https://example.com')

    assert client.is_closed
    assert transport.close_count == 1


@pytest.mark.asyncio
async def test_client_propagates_wrapped_transport_close_failure(mocker):
    transport = httpx.MockTransport(lambda request: httpx.Response(200))
    close = mocker.patch.object(transport, 'aclose', side_effect=RuntimeError('close failed'))
    client = KiotaClientFactory.create_with_default_middleware(
        httpx.AsyncClient(transport=transport, trust_env=False)
    )

    with pytest.raises(RuntimeError, match='close failed'):
        await client.aclose()

    close.assert_awaited_once()
