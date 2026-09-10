import pytest

from kiota_abstractions.base_request_configuration import (
    BaseRequestConfiguration,
    RequestConfiguration,
)


def test_base_request_configuration_deprecation_warning():
    with pytest.warns(DeprecationWarning, match="BaseRequestConfiguration is deprecated. Use RequestConfiguration class instead."):
        BaseRequestConfiguration()


def test_import_base_request_configuration_no_warning():
    from kiota_abstractions.base_request_configuration import BaseRequestConfiguration, RequestConfiguration
    assert len(pytest.warns()) == 0


def test_request_configurations_do_not_share_a_headers_collection():
    first = RequestConfiguration()
    second = RequestConfiguration()

    first.headers.add("Prefer", "outlook.body-content-type=text")

    assert first.headers is not second.headers
    assert second.headers.try_get("Prefer") is False
    assert RequestConfiguration().headers.count() == 0
