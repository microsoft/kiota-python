# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All Rights Reserved.
# Licensed under the MIT License.
# See License in the project root for license information.
# ------------------------------------------------------------------------------

from typing import Any

from ..request_information import RequestInformation
from .authentication_provider import AuthenticationProvider


class AnonymousAuthenticationProvider(AuthenticationProvider):
    """This authentication provider does not perform any authentication

    Args:
        AuthenticationProvider (ABC): The abstract base class that this class implements
    """

    async def authenticate_request(
        self,
        request: RequestInformation,
        additional_authentication_context: dict[str, Any] = {}
    ) -> None:
        """Authenticates the provided request information

        Args:
            request (RequestInformation): Request information object
            additional_authentication_context (dict):
        """
        return
