import pytest
from kiota_abstractions.authentication import AllowedHostsValidator

from kiota_authentication_azure.azure_identity_access_token_provider import (
    AzureIdentityAccessTokenProvider,
)

from .helpers import DummyAsyncAzureTokenCredential, DummySyncAzureTokenCredential


def test_invalid_instantiation_without_credentials():
    with pytest.raises(Exception):
        token_provider = AzureIdentityAccessTokenProvider(None)


def test_valid_instantiation_without_options():
    token_provider = AzureIdentityAccessTokenProvider(DummyAsyncAzureTokenCredential(), None)
    assert not token_provider._options


def test_invalid_instatiation_without_scopes():
    with pytest.raises(Exception):
        token_provider = AzureIdentityAccessTokenProvider(
            DummyAsyncAzureTokenCredential(), None, None
        )


def test_get_allowed_hosts_validator():
    token_provider = AzureIdentityAccessTokenProvider(DummySyncAzureTokenCredential(), None)
    validator = token_provider.get_allowed_hosts_validator()
    hosts = validator.get_allowed_hosts()
    assert isinstance(validator, AllowedHostsValidator)
    assert hosts == []

def test_get_allowed_hosts_validator_with_hosts():
    allowed_hosts = [
        'graph.microsoft.com', 'graph.microsoft.us', 'dod-graph.microsoft.us',
        'graph.microsoft.de', 'microsoftgraph.chinacloudapi.cn', 'canary.graph.microsoft.com'
    ]
    token_provider = AzureIdentityAccessTokenProvider(DummySyncAzureTokenCredential(), None, scopes=[], allowed_hosts=allowed_hosts)
    validator = token_provider.get_allowed_hosts_validator()
    hosts = validator.get_allowed_hosts()
    hosts.sort()
    allowed_hosts.sort()
    assert hosts == allowed_hosts
    assert isinstance(validator, AllowedHostsValidator)


@pytest.mark.asyncio
async def test_get_authorization_token_async():

    token_provider = AzureIdentityAccessTokenProvider(DummyAsyncAzureTokenCredential(), None)
    token = await token_provider.get_authorization_token('https://graph.microsoft.com')
    assert token == "This is a dummy token"


@pytest.mark.asyncio
async def test_get_authorization_token_sync():

    token_provider = AzureIdentityAccessTokenProvider(DummySyncAzureTokenCredential(), None)
    token = await token_provider.get_authorization_token('https://graph.microsoft.com')
    assert token == "This is a dummy token"


@pytest.mark.asyncio
async def test_get_authorization_token_invalid_url():

    token_provider = AzureIdentityAccessTokenProvider(DummyAsyncAzureTokenCredential(), None)
    token = await token_provider.get_authorization_token('')
    assert token == ""
    with pytest.raises(Exception):
        token = await token_provider.get_authorization_token('https://')


@pytest.mark.asyncio
async def test_get_authorization_token_invalid_scheme():
    with pytest.raises(Exception):
        token_provider = AzureIdentityAccessTokenProvider(DummySyncAzureTokenCredential(), None)
        token = await token_provider.get_authorization_token('http://graph.microsoft.com')
        
@pytest.mark.asyncio
async def test_get_authorization_token_localhost():
    token_provider = AzureIdentityAccessTokenProvider(DummySyncAzureTokenCredential(), None)
    token = await token_provider.get_authorization_token('HTTP://LOCALHOST:8080')
    assert token
    
