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


class RecordingSyncAzureTokenCredential(DummySyncAzureTokenCredential):
    """Sync credential that records the scopes passed to get_token."""

    def __init__(self):
        self.received_scopes: list[tuple[str, ...]] = []

    def get_token(self, *scopes, **kwargs):
        self.received_scopes.append(scopes)
        return super().get_token(*scopes, **kwargs)


@pytest.mark.asyncio
async def test_derived_scope_strips_userinfo_and_port():
    """The default `.default` scope passed to `get_token` must be derived
    from the hostname only — never include userinfo or
    a `:port` (which Entra ID rejects for `.default` scopes).
    """
    credential = RecordingSyncAzureTokenCredential()
    token_provider = AzureIdentityAccessTokenProvider(credential, None)

    await token_provider.get_authorization_token(
        'https://alice:secret@graph.microsoft.com:8443/v1.0/me'
    )

    assert credential.received_scopes == [('https://graph.microsoft.com/.default',)]


@pytest.mark.asyncio
async def test_derived_scope_is_not_cached_across_hosts():
    """The first URL's derived scope must not be reused for later URLs.

    Previously the scope was assigned to `self._scopes`, making it sticky for
    the lifetime of the provider instance and causing tokens to be requested
    for the wrong audience after the first call.
    """
    credential = RecordingSyncAzureTokenCredential()
    token_provider = AzureIdentityAccessTokenProvider(credential, None)

    await token_provider.get_authorization_token('https://graph.microsoft.com/v1.0/me')
    await token_provider.get_authorization_token('https://graph.microsoft.us/v1.0/me')

    assert credential.received_scopes == [
        ('https://graph.microsoft.com/.default',),
        ('https://graph.microsoft.us/.default',),
    ]
    # Provider must not have mutated the caller-supplied scopes list.
    assert token_provider._scopes == []


@pytest.mark.asyncio
async def test_explicit_scopes_are_respected():
    credential = RecordingSyncAzureTokenCredential()
    token_provider = AzureIdentityAccessTokenProvider(
        credential, None, scopes=['https://graph.microsoft.com/.default']
    )

    await token_provider.get_authorization_token('https://graph.microsoft.com/v1.0/me')
    await token_provider.get_authorization_token('https://graph.microsoft.us/v1.0/me')

    assert credential.received_scopes == [
        ('https://graph.microsoft.com/.default',),
        ('https://graph.microsoft.com/.default',),
    ]

