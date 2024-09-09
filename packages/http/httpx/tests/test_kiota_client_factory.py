import httpx
import pytest

from kiota_http.kiota_client_factory import KiotaClientFactory
from kiota_http.middleware import (
    AsyncKiotaTransport,
    MiddlewarePipeline,
    ParametersNameDecodingHandler,
    RedirectHandler,
    RetryHandler,
    UrlReplaceHandler,
    HeadersInspectionHandler
)
from kiota_http.middleware.options import RedirectHandlerOption, RetryHandlerOption
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
        "http://": "http://localhost:8030",
        "https://": "http://localhost:8031",
    }
    timeout = httpx.Timeout(20, connect=10)
    custom_client = httpx.AsyncClient(timeout=timeout, http2=True, proxies=proxies)
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
    assert isinstance(pipeline._first_middleware, RedirectHandler)
    retry_handler = pipeline._first_middleware.next
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
        "http://": "http://localhost:8030",
        "https://": "http://localhost:8031",
    }
    timeout = httpx.Timeout(20, connect=10)
    custom_client = httpx.AsyncClient(timeout=timeout, http2=True, proxies=proxies)
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

    assert len(middleware) == 6
    assert isinstance(middleware[0], RedirectHandler)
    assert isinstance(middleware[1], RetryHandler)
    assert isinstance(middleware[2], ParametersNameDecodingHandler)
    assert isinstance(middleware[3], UrlReplaceHandler)
    assert isinstance(middleware[4], UserAgentHandler)
    assert isinstance(middleware[5], HeadersInspectionHandler)


def test_get_default_middleware_with_options():
    """Test fetching of default middleware with custom options passed"""
    retry_options = RetryHandlerOption(max_retries=7)
    redirect_options = RedirectHandlerOption(should_redirect=False)
    options = {
        f'{retry_options.get_key()}': retry_options,
        f'{redirect_options.get_key()}': redirect_options
    }

    middleware = KiotaClientFactory.get_default_middleware(options=options)

    assert len(middleware) == 6
    assert isinstance(middleware[0], RedirectHandler)
    assert middleware[0].options.should_redirect is False
    assert isinstance(middleware[1], RetryHandler)
    assert middleware[1].options.max_retry == 7
    assert isinstance(middleware[2], ParametersNameDecodingHandler)


def test_create_middleware_pipeline():

    middleware = KiotaClientFactory.get_default_middleware(None)
    pipeline = KiotaClientFactory.create_middleware_pipeline(
        middleware,
        httpx.AsyncClient()._transport
    )

    assert isinstance(pipeline, MiddlewarePipeline)
