import pytest

from kiota_abstractions.authentication import ApiKeyAuthenticationProvider, AuthenticationProvider, KeyLocation

allowed_hosts = ["example.com"]


def test_initialization():
    provider = ApiKeyAuthenticationProvider(
        KeyLocation.Header, "test_key_string", "api_key", allowed_hosts
    )

    assert isinstance(provider, AuthenticationProvider)


def test_arguments():
    key_location_error = "^key_location can only be 'query_parameter' or 'header'$"
    with pytest.raises(ValueError, match=key_location_error):
        ApiKeyAuthenticationProvider("body", "test_key_string", "api_key", allowed_hosts)

    api_key_error = "^api_key can only be a string but you supplied ''$"
    with pytest.raises(ValueError, match=api_key_error):
        ApiKeyAuthenticationProvider(KeyLocation.Header, "", "api_key", allowed_hosts)

    parameter_key_error = "^parameter_name can only be a string but you supplied 123$"
    with pytest.raises(ValueError, match=parameter_key_error):
        ApiKeyAuthenticationProvider(KeyLocation.Header, "test_key_string", 123, allowed_hosts)
    allowed_hosts_error = "^Allowed hosts must be a list of strings$"
    with pytest.raises(TypeError, match=allowed_hosts_error):
        ApiKeyAuthenticationProvider(KeyLocation.Header, "test_key_string", "api_key", "")


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
    assert "api_key" in mock_request_information.request_headers
    assert mock_request_information.headers.get("api_key") == {"test_key_string"}


def test_https_prefix_in_allowed_host():
    with pytest.raises(
        ValueError, match="Allowed host value cannot contain 'https://' or 'http://' prefix"
    ):
        ApiKeyAuthenticationProvider(
            KeyLocation.Header, "test_key_string", "api_key", ["https://example.com"]
        )


def test_http_prefix_in_allowed_host():
    with pytest.raises(
        ValueError, match="Allowed host value cannot contain 'https://' or 'http://' prefix"
    ):
        ApiKeyAuthenticationProvider(
            KeyLocation.Header, "test_key_string", "api_key", ["http://example.com"]
        )


@pytest.mark.asyncio
async def test_unallowed_host_returns_early_without_adding_key(mock_request_information):
    provider = ApiKeyAuthenticationProvider(
        KeyLocation.Header,
        "test_key_string",
        "api_key",
        ["example.com"],
    )
    mock_request_information.url = "https://disallowed.com/api"
    await provider.authenticate_request(mock_request_information)
    assert not mock_request_information.headers.contains("api_key")


@pytest.mark.asyncio
async def test_unallowed_host_query_parameter_returns_early(mock_request_information):
    provider = ApiKeyAuthenticationProvider(
        KeyLocation.QueryParameter,
        "test_key_string",
        "api_key",
        ["example.com"],
    )
    original_url = "https://disallowed.com/api?existing=value"
    mock_request_information.url = original_url
    await provider.authenticate_request(mock_request_information)
    assert mock_request_information.url == original_url


@pytest.mark.asyncio
async def test_subdomain_unallowed_host_returns_early(mock_request_information):
    provider = ApiKeyAuthenticationProvider(
        KeyLocation.Header,
        "test_key_string",
        "api_key",
        ["example.com"],
    )
    mock_request_information.url = "https://subdomain.example.com/api"
    await provider.authenticate_request(mock_request_information)
    assert not mock_request_information.headers.contains("api_key")


@pytest.mark.asyncio
async def test_header_location_initializes_none_headers(mock_request_information):
    provider = ApiKeyAuthenticationProvider(
        KeyLocation.Header,
        "test_key_string",
        "api_key",
        ["example.com"],
    )
    mock_request_information.headers = None
    await provider.authenticate_request(mock_request_information)
    assert mock_request_information.headers is not None
    assert mock_request_information.headers.get("api_key") == {"test_key_string"}


@pytest.mark.asyncio
async def test_query_parameter_preserves_blank_and_existing_parameters(mock_request_information):
    provider = ApiKeyAuthenticationProvider(
        KeyLocation.QueryParameter,
        "test_key_string",
        "api_key",
        ["example.com"],
    )
    mock_request_information.url = "https://example.com/api?flag&page=1"
    await provider.authenticate_request(mock_request_information)
    assert "flag" in mock_request_information.url
    assert "page=1" in mock_request_information.url
    assert "api_key=test_key_string" in mock_request_information.url


def test_default_allowed_hosts_does_not_share_state():
    p1 = ApiKeyAuthenticationProvider(KeyLocation.Header, "key1", "param1")
    p2 = ApiKeyAuthenticationProvider(KeyLocation.Header, "key2", "param2")
    assert len(p1.allowed_hosts_validator.allowed_hosts) == 0
    assert len(p2.allowed_hosts_validator.allowed_hosts) == 0


@pytest.mark.asyncio
async def test_authenticate_request_none_request_raises():
    provider = ApiKeyAuthenticationProvider(KeyLocation.Header, "key", "param")
    with pytest.raises(ValueError, match="request can not be empty"):
        await provider.authenticate_request(None)
