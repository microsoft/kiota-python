import pytest

from kiota_http._version import VERSION
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
