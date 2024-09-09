from dataclasses import dataclass
from azure.core.credentials import AccessToken


class DummyToken(AccessToken):
    """A dummy token from the base AccessToken tuple"""


class DummySyncAzureTokenCredential:
    """Helper to mock getting a token synchronously."""

    def get_token(self, *args, **kwargs):
        return DummyToken(token="This is a dummy token", expires_on=123)


class DummyAsyncAzureTokenCredential:
    """Helper to mock getting a token asynchronously."""

    async def get_token(self, *args, **kwargs):
        return DummyToken(token="This is a dummy token", expires_on=123)

    async def close(self, *args):
        pass
