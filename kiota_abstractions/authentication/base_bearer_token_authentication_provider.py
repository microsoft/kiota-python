# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All Rights Reserved.
# Licensed under the MIT License.
# See License in the project root for license information.
# ------------------------------------------------------------------------------

from typing import Any, Dict

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
        additional_authentication_context: Dict[str, Any] = {}
    ) -> None:
        """Authenticates the provided RequestInformation instance using the provided
        authorization token

        Args:
            request (RequestInformation): Request information object
        """
        if not request:
            raise Exception("Request cannot be null")
        if all(
            [
                additional_authentication_context, self.CLAIMS_KEY
                in additional_authentication_context, self.AUTHORIZATION_HEADER in request.headers
            ]
        ):
            del request.headers[self.AUTHORIZATION_HEADER]

        if not request.request_headers:
            request.headers = {}

        if not self.AUTHORIZATION_HEADER in request.headers:
            token = await self.access_token_provider.get_authorization_token(
                request.url, additional_authentication_context
            )
            if token:
                request.add_request_headers({f'{self.AUTHORIZATION_HEADER}': f'Bearer {token}'})
