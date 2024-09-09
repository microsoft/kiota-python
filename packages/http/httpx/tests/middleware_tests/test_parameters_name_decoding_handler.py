import httpx
import pytest

from kiota_http.middleware import ParametersNameDecodingHandler
from kiota_http.middleware.options import ParametersNameDecodingHandlerOption

OPTION_KEY = "ParametersNameDecodingHandlerOption"
def test_no_config():
    """
    Test that default values are used if no custom confguration is passed
    """
    handler = ParametersNameDecodingHandler()
    assert handler.options.enabled is True
    assert handler.options.characters_to_decode == [".", "-", "~", "$"]
    assert handler.options.get_key() == OPTION_KEY


def test_custom_options():
    """
    Test that default configuration is overrriden if custom configuration is provided
    """
    options = ParametersNameDecodingHandlerOption(
        enable=False, characters_to_decode=[".", "-"]
    )
    handler = ParametersNameDecodingHandler(options)

    assert handler.options.enabled is not True
    assert "$" not in handler.options.characters_to_decode
    assert handler.options.get_key() == OPTION_KEY


@pytest.mark.asyncio
async def test_decodes_query_parameter_names_only():
    """
    Test that only query parameter names are decoded
    """
    encoded_decoded = [
    ("http://localhost?%24select=diplayName&api%2Dversion=2", "http://localhost?$select=diplayName&api-version=2"),
    ("http://localhost?%24select=diplayName&api%7Eversion=2", "http://localhost?$select=diplayName&api~version=2"),
    ("http://localhost?%24select=diplayName&api%2Eversion=2", "http://localhost?$select=diplayName&api.version=2"),
    ("http://localhost:888?%24select=diplayName&api%2Dversion=2", "http://localhost:888?$select=diplayName&api-version=2"),
    ("http://localhost", "http://localhost"),
    ("https://google.com/?q=1%2b2", "https://google.com/?q=1%2b2"),
    ("https://google.com/?q=M%26A", "https://google.com/?q=M%26A"),
    ("https://google.com/?q=1%2B2", "https://google.com/?q=1%2B2"), # Values are not decoded
    ("https://google.com/?q=M%26A", "https://google.com/?q=M%26A"), # Values are not decoded
    ("https://google.com/?q%2D1=M%26A", "https://google.com/?q-1=M%26A"), # Values are not decoded but params are
    ("https://google.com/?q%2D1&q=M%26A=M%26A", "https://google.com/?q-1&q=M%26A=M%26A"), # Values are not decoded but params are
    ("https://graph.microsoft.com?%24count=true&query=%24top&created%2Din=2022-10-05&q=1%2b2&q2=M%26A&subject%2Ename=%7eWelcome&%24empty",
     "https://graph.microsoft.com?$count=true&query=%24top&created-in=2022-10-05&q=1%2b2&q2=M%26A&subject.name=%7eWelcome&$empty")
    ]
    
    def request_handler(request: httpx.Request):
        return httpx.Response(200, json={"text": "Hello, world!"})
    
    handler = ParametersNameDecodingHandler()
    for encoded, decoded in encoded_decoded:
        request = httpx.Request('GET', encoded)
        mock_transport = httpx.MockTransport(request_handler)
        resp = await handler.send(request, mock_transport)
        assert str(resp.request.url) == decoded
