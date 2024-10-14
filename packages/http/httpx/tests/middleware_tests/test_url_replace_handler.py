import httpx
import pytest

from kiota_http.middleware import UrlReplaceHandler
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
