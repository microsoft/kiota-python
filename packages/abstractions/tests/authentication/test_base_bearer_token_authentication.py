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
    assert mock_request_information.headers.get_all() == {'authorization': {'Bearer SomeToken'}}
    assert mock_request_information.request_headers == {'authorization': 'Bearer SomeToken'}


@pytest.mark.asyncio
async def test_authenticate_request_null_request_raises_value_error(mock_access_token_provider):
    auth = BaseBearerTokenAuthenticationProvider(mock_access_token_provider)
    with pytest.raises(ValueError, match="^Request cannot be null$"):
        await auth.authenticate_request(None)


@pytest.mark.asyncio
async def test_authenticate_request_initializes_none_headers(
    mock_request_information, mock_access_token_provider
):
    auth = BaseBearerTokenAuthenticationProvider(mock_access_token_provider)
    mock_request_information.headers = None
    await auth.authenticate_request(mock_request_information)

    assert mock_request_information.headers is not None
    assert mock_request_information.headers.contains("Authorization")
    assert mock_request_information.headers.get("Authorization") == {"Bearer SomeToken"}


@pytest.mark.asyncio
async def test_authenticate_request_with_none_additional_context(
    mock_request_information, mock_access_token_provider
):
    auth = BaseBearerTokenAuthenticationProvider(mock_access_token_provider)
    await auth.authenticate_request(
        mock_request_information, additional_authentication_context=None
    )

    assert mock_request_information.headers.contains("Authorization")
    assert mock_request_information.headers.get("Authorization") == {"Bearer SomeToken"}


@pytest.mark.asyncio
async def test_authenticate_request_claims_removes_existing_authorization(
    mock_request_information, mock_access_token_provider
):
    auth = BaseBearerTokenAuthenticationProvider(mock_access_token_provider)
    mock_request_information.headers.add("Authorization", "Bearer OldToken")
    await auth.authenticate_request(
        mock_request_information, additional_authentication_context={"claims": "some_claims"}
    )

    assert mock_request_information.headers.get("Authorization") == {"Bearer SomeToken"}


@pytest.mark.asyncio
async def test_authenticate_request_preserves_existing_authorization_without_claims(
    mock_request_information, mock_access_token_provider
):
    auth = BaseBearerTokenAuthenticationProvider(mock_access_token_provider)
    mock_request_information.headers.add("Authorization", "Bearer ExistingToken")
    await auth.authenticate_request(mock_request_information)

    assert mock_request_information.headers.get("Authorization") == {"Bearer ExistingToken"}
