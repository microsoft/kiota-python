import pytest

from kiota_abstractions.authentication.access_token_provider import AccessTokenProvider
from kiota_abstractions.authentication.allowed_hosts_validator import AllowedHostsValidator
from kiota_abstractions.request_information import RequestInformation


class MockAccessTokenProvider(AccessTokenProvider):

    def __init__(self):
        self.token = None

    async def get_authorization_token(self, url: str) -> str:
        return "SomeToken"

    def get_allowed_hosts_validator(self) -> AllowedHostsValidator:
        return AllowedHostsValidator(["example.com"])


@pytest.fixture
def mock_request_information():
    request_info = RequestInformation()
    request_info.url = "https://example.com"
    return request_info


@pytest.fixture
def mock_access_token_provider():
    return MockAccessTokenProvider()
