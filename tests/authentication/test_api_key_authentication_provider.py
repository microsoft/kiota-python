import pytest

from kiota_abstractions.authentication import (
    ApiKeyAuthenticationProvider,
    KeyLocation,
    AuthenticationProvider,
)


def test_initialization():
    provider = ApiKeyAuthenticationProvider(
        KeyLocation.Header, "test_key_string", "api_key", ["example.com"]
    )

    assert isinstance(provider, AuthenticationProvider)


def test_arguments():
    key_location_error = "^key_location can only be 'query_parameter' or 'header'$"
    with pytest.raises(ValueError, match=key_location_error):
        ApiKeyAuthenticationProvider(
            "body", "test_key_string", "api_key", ["example.com"]
        )

    api_key_error = "^api_key can only be a string but you supplied ''$"
    with pytest.raises(ValueError, match=api_key_error):
        ApiKeyAuthenticationProvider(KeyLocation.Header, "", "api_key", ["example.com"])

    parameter_key_error = "^parameter_name can only be a string but you supplied 123$"
    with pytest.raises(ValueError, match=parameter_key_error):
        ApiKeyAuthenticationProvider(
            KeyLocation.Header, "test_key_string", 123, ["example.com"]
        )
    allowed_hosts_error = "^Allowed hosts must be a list of strings$"
    with pytest.raises(TypeError, match=allowed_hosts_error):
        ApiKeyAuthenticationProvider(
            KeyLocation.Header, "test_key_string", "api_key", ""
        )
