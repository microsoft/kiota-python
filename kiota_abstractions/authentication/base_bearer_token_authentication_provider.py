# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All Rights Reserved.
# Licensed under the MIT License.
# See License in the project root for license information.
# ------------------------------------------------------------------------------

import re
import time
from typing import Any, Dict, Optional

import jwt

from ..headers_collection import HeadersCollection
from ..request_information import RequestInformation
from .access_token_provider import AccessTokenProvider
from .authentication_provider import AuthenticationProvider


class BaseBearerTokenAuthenticationProvider(AuthenticationProvider):
    """Provides a base class for implementing AuthenticationProvider for Bearer token scheme."""

    AUTHORIZATION_HEADER = "Authorization"
    CLAIMS_KEY = "claims"
    AUTHORIZATION_PREFIX = "Bearer"

    def __init__(self, access_token_provider: AccessTokenProvider) -> None:
        self.access_token_provider = access_token_provider

    async def authenticate_request(
        self,
        request: RequestInformation,
        additional_authentication_context: Dict[str, Any] = None,
    ) -> None:
        """Authenticates the provided RequestInformation instance using the provided
        authorization token

        Args:
            request (RequestInformation): Request information object
        """
        if not request:
            raise Exception("Request cannot be null")

        if not request.request_headers:
            request.headers = HeadersCollection()

        if additional_authentication_context:
            self._check_for_claims_key(request, additional_authentication_context)

        self._remove_expired_token(request)

        if not request.headers.contains(self.AUTHORIZATION_HEADER):
            token = await self.access_token_provider.get_authorization_token(
                request.url, additional_authentication_context
            )
            if token:
                request.headers.add(
                    f"{self.AUTHORIZATION_HEADER}",
                    f"{self.AUTHORIZATION_PREFIX} {token}",
                )
            return

    def _check_for_claims_key(
        self,
        request: RequestInformation,
        additional_authentication_context: Dict[str, Any],
    ) -> None:
        """
        Checks if the claims key is in the additional authentication context and if the 
        authorization header is in the request headers. If both conditions are met, it removes 
        the authorization header from the request headers.

        Args:
            request (RequestInformation): The request information object.
            additional_authentication_context (Dict[str, Any]): Additional context for authentication.
        """

        if all(
            [
                self.CLAIMS_KEY in additional_authentication_context,
                request.headers.contains(self.AUTHORIZATION_HEADER),
            ]
        ):
            request.headers.remove(self.AUTHORIZATION_HEADER)

    def _remove_expired_token(self, request: RequestInformation) -> None:
        """
        Removes expired tokens from the request headers.

        Args:
            request (RequestInformation): The request information object.
        """

        tokens = request.headers.get(self.AUTHORIZATION_HEADER)

        if tokens:
            for _token in tokens:
                matchs = re.match(rf"{self.AUTHORIZATION_PREFIX} (.*)", _token)
                if matchs:
                    token = matchs.group(0).split(" ")[1]
                    if self.is_token_expired(token):
                        request.headers.remove(self.AUTHORIZATION_HEADER)

    @staticmethod
    def is_token_expired(token: str) -> bool:
        """
        Checks if the given token is expired.

        Args:
            token (str): The token to check.

        Returns:
            bool: True if the token is expired, False otherwise.
        """

        try:
            payload: Dict[str, Any] = jwt.decode(
                token, options={"verify_signature": False}
            )

            # Get the expiration time (exp), which is a Unix timestamp
            exp: Optional[int] = payload.get("exp", None)

            # Check if the current time is past the token's expiration
            if exp is not None and time.time() >= exp:
                return True
            return False
        except jwt.DecodeError:
            return True  # If we can't decode the token, consider it as expired
