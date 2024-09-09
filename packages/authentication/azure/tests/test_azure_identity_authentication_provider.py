import pytest
from kiota_abstractions.request_information import RequestInformation

from kiota_authentication_azure.azure_identity_authentication_provider import (
    AzureIdentityAuthenticationProvider,
)
from unittest.mock import MagicMock

from .helpers import DummyAsyncAzureTokenCredential, DummySyncAzureTokenCredential


def test_invalid_instantiation_without_credentials():
    with pytest.raises(Exception):
        auth_provider = AzureIdentityAuthenticationProvider(None)


@pytest.mark.asyncio
async def test_valid_instantiation_without_options():
    auth_provider = AzureIdentityAuthenticationProvider(DummyAsyncAzureTokenCredential())
    request_info = RequestInformation()
    request_info.url = "https://graph.microsoft.com"
    await auth_provider.authenticate_request(request_info)
    assert isinstance(auth_provider, AzureIdentityAuthenticationProvider)
    assert 'authorization' in request_info.request_headers


@pytest.mark.asyncio
async def test_adds_claim_to_the_token_context(mocker):
    credential = DummyAsyncAzureTokenCredential()
    mocker.patch.object(credential, 'get_token', autospec=True)
    auth_provider = AzureIdentityAuthenticationProvider(credential)

    request_info = RequestInformation()
    request_info.url = "https://graph.microsoft.com"
    await auth_provider.authenticate_request(
        request_info, {
            "claims":
            "eyJhY2Nlc3NfdG9rZW4iOnsibmJmIjp7ImVzc2VudGlhbCI6dHJ1ZSwgInZhbHVlIjoiMTY1MjgxMzUwOCJ9fX0="
        }
    )
    assert isinstance(auth_provider, AzureIdentityAuthenticationProvider)
    credential.get_token.assert_called_once_with(
        'https://graph.microsoft.com/.default',
        claims="""{"access_token":{"nbf":{"essential":true, "value":"1652813508"}}}""",
        enable_cae=True
    )
