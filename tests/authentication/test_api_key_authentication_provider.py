import pytest

from kiota_abstractions.authentication import (
    ApiKeyAuthenticationProvider,
    KeyLocation,
    AuthenticationProvider,
)

allowed_hosts = ["https://example.com"]


def test_initialization():
    provider = ApiKeyAuthenticationProvider(
        KeyLocation.Header, "test_key_string", "api_key", allowed_hosts
    )

    assert isinstance(provider, AuthenticationProvider)


def test_arguments():
    key_location_error = "^key_location can only be 'query_parameter' or 'header'$"
    with pytest.raises(ValueError, match=key_location_error):
        ApiKeyAuthenticationProvider(
            "body", "test_key_string", "api_key", allowed_hosts
        )

    api_key_error = "^api_key can only be a string but you supplied ''$"
    with pytest.raises(ValueError, match=api_key_error):
        ApiKeyAuthenticationProvider(KeyLocation.Header, "", "api_key", allowed_hosts)

    parameter_key_error = "^parameter_name can only be a string but you supplied 123$"
    with pytest.raises(ValueError, match=parameter_key_error):
        ApiKeyAuthenticationProvider(
            KeyLocation.Header, "test_key_string", 123, allowed_hosts
        )
    allowed_hosts_error = "^Allowed hosts must be a list of strings$"
    with pytest.raises(TypeError, match=allowed_hosts_error):
        ApiKeyAuthenticationProvider(
            KeyLocation.Header, "test_key_string", "api_key", ""
        )


@pytest.mark.asyncio
async def test_query_parameter_location_authentication(mock_request_information):
    provider = ApiKeyAuthenticationProvider(
        KeyLocation.QueryParameter,
        "test_key_string",
        "api_key",
        allowed_hosts,
    )
    await provider.authenticate_request(mock_request_information)
    assert mock_request_information.url == "https://example.com?api_key=test_key_string"


@pytest.mark.asyncio
async def test_header_location_authentication(mock_request_information):
    provider = ApiKeyAuthenticationProvider(
        KeyLocation.Header,
        "test_key_string",
        "api_key",
        allowed_hosts,
    )
    await provider.authenticate_request(mock_request_information)
    assert "api_key" in mock_request_information.headers
    assert mock_request_information.headers["api_key"] == {"test_key_string"}
