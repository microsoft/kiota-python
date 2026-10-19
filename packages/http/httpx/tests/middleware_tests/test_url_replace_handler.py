import httpx
import pytest

from kiota_http.middleware import REQUEST_OPTIONS_KEY, UrlReplaceHandler
from kiota_http.middleware.options import UrlReplaceHandlerOption

ORIGINAL_URL = "https://graph.microsoft.com/users/user-id-to-replace/messages"
REPLACED_URL = "https://graph.microsoft.com/me/messages"


def test_no_config():
    """
    Test that default values are used if no custom confguration is passed
    """
    handler = UrlReplaceHandler()
    assert handler.options.is_enabled is True
    assert handler.options.replacement_pairs == {}
    assert handler.options.get_key() == "UrlReplaceHandlerOption"
    assert handler.replace_url_segment(ORIGINAL_URL, handler.options) == ORIGINAL_URL


def test_custom_options_with_handler_disabled():
    """
    Test that default configuration is overrriden if custom configuration is provided
    """
    handler = UrlReplaceHandler(
        options=UrlReplaceHandlerOption(
            enabled=False, replacement_pairs={"/users/user-id-to-replace": "/me"}
        )
    )

    assert not handler.options.is_enabled
    assert handler.options.replacement_pairs
    assert handler.replace_url_segment(ORIGINAL_URL, handler.options) == ORIGINAL_URL


def test_replace_url_segment():
    """
    Test that url segments corresponding to replacement pairs are replaced.
    """
    handler = UrlReplaceHandler(
        options=UrlReplaceHandlerOption(
            enabled=True, replacement_pairs={"/users/user-id-to-replace": "/me"}
        )
    )

    assert handler.options.is_enabled
    assert handler.options.replacement_pairs
    assert handler.options.get_key() == "UrlReplaceHandlerOption"
    assert handler.replace_url_segment(ORIGINAL_URL, handler.options) == REPLACED_URL


def test_default_replacement_pairs_are_not_shared():
    UrlReplaceHandlerOption().replacement_pairs["/users/user-id-to-replace"] = "/me"
    assert UrlReplaceHandlerOption().replacement_pairs == {}


@pytest.mark.asyncio
async def test_request_option_enables_replacement():
    option = UrlReplaceHandlerOption(
        enabled=True, replacement_pairs={"/users/user-id-to-replace": "/me"}
    )
    request = httpx.Request(
        "GET", ORIGINAL_URL, extensions={REQUEST_OPTIONS_KEY: {option.get_key(): option}}
    )
    handler = UrlReplaceHandler(options=UrlReplaceHandlerOption(enabled=False))

    async with httpx.MockTransport(lambda request: httpx.Response(200)) as transport:
        response = await handler.send(request, transport)

    assert str(response.request.url) == REPLACED_URL


@pytest.mark.asyncio
async def test_span_ends_on_transport_failure(span_exporter):

    def request_handler(request):
        raise httpx.ReadError("request interrupted")

    handler = UrlReplaceHandler()
    request = httpx.Request("GET", ORIGINAL_URL)
    async with httpx.MockTransport(request_handler) as transport:
        with pytest.raises(httpx.ReadError):
            await handler.send(request, transport)

    assert [span.name for span in span_exporter.get_finished_spans()] == ["UrlReplaceHandler_send"]
