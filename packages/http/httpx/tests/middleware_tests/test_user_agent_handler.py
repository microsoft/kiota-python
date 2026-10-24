import httpx
import pytest

from kiota_http._version import VERSION
from kiota_http.middleware import REQUEST_OPTIONS_KEY, UserAgentHandler
from kiota_http.middleware.options.user_agent_handler_option import UserAgentHandlerOption


def test_no_config():
    """
    Ensures the User Agent defaults are set.
    """
    options = UserAgentHandlerOption()
    assert options.is_enabled
    assert options.product_name == 'kiota-python'
    assert options.product_version == VERSION


def test_custom_config():
    """
    Ensures that setting is_enabled to False.
    """

    options = UserAgentHandlerOption(enabled=False)
    assert not options.is_enabled


def test_is_enabled_setter():
    options = UserAgentHandlerOption()
    options.is_enabled = False
    assert not options.is_enabled


@pytest.mark.asyncio
async def test_request_option_sets_the_product():
    option = UserAgentHandlerOption(product_name="custom", product_version="9")
    request = httpx.Request(
        "GET", "https://example.com", extensions={REQUEST_OPTIONS_KEY: {option.get_key(): option}}
    )

    async with httpx.MockTransport(lambda request: httpx.Response(200)) as transport:
        response = await UserAgentHandler().send(request, transport)

    assert response.request.headers["User-Agent"] == "custom/9"

@pytest.mark.asyncio
async def test_user_agent_handler_null_request_raises():
    handler = UserAgentHandler()
    with pytest.raises(TypeError, match="request cannot be null"):
        await handler.send(None, httpx.MockTransport(lambda req: httpx.Response(200)))


@pytest.mark.asyncio
async def test_user_agent_handler_span_encloses_transport(span_exporter):
    def request_handler(request):
        assert len(span_exporter.get_finished_spans()) == 0
        return httpx.Response(200)

    handler = UserAgentHandler()
    request = httpx.Request("GET", "https://example.com")
    async with httpx.MockTransport(request_handler) as transport:
        resp = await handler.send(request, transport)

    assert resp.status_code == 200
    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    assert spans[0].name == "UserAgentHandler_send"


@pytest.mark.asyncio
async def test_user_agent_handler_span_records_exception_on_transport_failure(span_exporter):
    def request_handler(request):
        raise httpx.ReadError("connection failed")

    handler = UserAgentHandler()
    request = httpx.Request("GET", "https://example.com")
    async with httpx.MockTransport(request_handler) as transport:
        with pytest.raises(httpx.ReadError):
            await handler.send(request, transport)

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    assert spans[0].name == "UserAgentHandler_send"
    assert len(spans[0].events) > 0
    assert spans[0].events[0].name == "exception"
