import pytest

from kiota_abstractions.authentication import BaseBearerTokenAuthenticationProvider


def test_initialization(mock_access_token_provider):
    auth = BaseBearerTokenAuthenticationProvider(mock_access_token_provider)
    assert auth.access_token_provider == mock_access_token_provider


@pytest.mark.asyncio
async def test_authenticate_request_null_request_information(mock_access_token_provider):
    auth = BaseBearerTokenAuthenticationProvider(mock_access_token_provider)

    with pytest.raises(Exception):
        await auth.authenticate_request(None)


@pytest.mark.asyncio
async def test_authenticate_request(mock_request_information, mock_access_token_provider):
    auth = BaseBearerTokenAuthenticationProvider(mock_access_token_provider)
    await auth.authenticate_request(mock_request_information)

    assert mock_request_information
    assert mock_request_information.headers == {'authorization': {'Bearer SomeToken'}}
    assert mock_request_information.request_headers == {'authorization': 'Bearer SomeToken'}
