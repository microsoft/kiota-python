import pytest

from kiota_abstractions.base_request_configuration import BaseRequestConfiguration


def test_base_request_configuration_deprecation_warning():
    with pytest.warns(DeprecationWarning, match="BaseRequestConfiguration is deprecated. Use RequestConfiguration class instead."):
        BaseRequestConfiguration()


def test_import_base_request_configuration_no_warning():
    from kiota_abstractions.base_request_configuration import BaseRequestConfiguration, RequestConfiguration
    assert len(pytest.warns()) == 0
