# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All Rights Reserved.
# Licensed under the MIT License.
# See License in the project root for license information.
# ------------------------------------------------------------------------------

from abc import ABC, abstractmethod
from typing import Any

from ..request_information import RequestInformation


class AuthenticationProvider(ABC):
    """
    Base class for providing authentication information for a request.
    """

    @abstractmethod
    async def authenticate_request(
        self,
        request: RequestInformation,
        additional_authentication_context: dict[str, Any] = {}
    ) -> None:
        """Authenticates the application request

        Args:
            request (RequestInformation): The request to authenticate
            additional_authentication_context (dict):
        """
        pass
