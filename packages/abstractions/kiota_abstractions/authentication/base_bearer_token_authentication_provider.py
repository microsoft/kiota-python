# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All Rights Reserved.
# Licensed under the MIT License.
# See License in the project root for license information.
# ------------------------------------------------------------------------------

from typing import Any, Optional

from ..headers_collection import HeadersCollection
from ..request_information import RequestInformation
from .access_token_provider import AccessTokenProvider
from .authentication_provider import AuthenticationProvider


class BaseBearerTokenAuthenticationProvider(AuthenticationProvider):
    """Provides a base class for implementing AuthenticationProvider for Bearer token scheme.
    """
    AUTHORIZATION_HEADER = "Authorization"
    CLAIMS_KEY = "claims"

    def __init__(self, access_token_provider: AccessTokenProvider) -> None:
        self.access_token_provider = access_token_provider

    async def authenticate_request(
        self,
        request: RequestInformation,
        additional_authentication_context: Optional[dict[str, Any]] = None,
    ) -> None:
        """Authenticates the provided RequestInformation instance using the provided
        authorization token

        Args:
            request (RequestInformation): Request information object
        """
        if not request:
            raise ValueError("Request cannot be null")

        if request.headers is None:
            request.headers = HeadersCollection()

        if additional_authentication_context is None:
            additional_authentication_context = {}

        if (
            self.CLAIMS_KEY in additional_authentication_context
            and request.headers.contains(self.AUTHORIZATION_HEADER)
        ):
            request.headers.remove(self.AUTHORIZATION_HEADER)

        if not request.headers.contains(self.AUTHORIZATION_HEADER):
            token = await self.access_token_provider.get_authorization_token(
                request.url, additional_authentication_context
            )
            if token:
                request.headers.add(self.AUTHORIZATION_HEADER, f'Bearer {token}')
