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
