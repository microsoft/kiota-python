# ------------------------------------
# Copyright (c) Microsoft Corporation. All Rights Reserved.
# Licensed under the MIT License.
# See License in the project root for license information.
# ------------------------------------

from typing import Optional

import httpx

from .middleware import BaseMiddleware
from .options import BodyInspectionHandlerOption

BODY_INSPECTION_KEY = "com.microsoft.kiota.handler.body_inspection.enable"


class BodyInspectionHandler(BaseMiddleware):
    """The Body Inspection Handler allows the developer to inspect the body of the
    request and response.
    """

    def __init__(
        self,
        options: Optional[BodyInspectionHandlerOption] = None,
    ):
        """Create an instance of BodyInspectionHandler

        Args:
            options (BodyInspectionHandlerOption, optional): Default options to apply to the
            handler. A new BodyInspectionHandlerOption per handler when not provided.
        """
        super().__init__()
        self.options = options if options is not None else BodyInspectionHandlerOption()

    async def send(
        self, request: httpx.Request, transport: httpx.AsyncBaseTransport
    ) -> httpx.Response:
        """To execute the current middleware

        Args:
            request (httpx.Request): The prepared request object
            transport (httpx.AsyncBaseTransport): The HTTP transport to use

        Returns:
            httpx.Response: The response object.
        """
        current_options = self._get_current_options(request)
        span = self._create_observability_span(request, "BodyInspectionHandler_send")
        span.set_attribute(BODY_INSPECTION_KEY, True)
        span.end()

        if current_options and current_options.inspect_request_body:
            content = await request.aread()
            if content:
                current_options.request_body = content
            else:
                current_options.request_body = None

        response = await super().send(request, transport)

        if current_options and current_options.inspect_response_body:
            content = await response.aread()
            if content:
                current_options.response_body = content
            else:
                current_options.response_body = None

        return response

    def _get_current_options(self, request: httpx.Request) -> BodyInspectionHandlerOption:
        """Returns the options to use for the request. Overrides default options if
        request options are passed.

        Args:
            request (httpx.Request): The prepared request object

        Returns:
            BodyInspectionHandlerOption: The options to be used.
        """
        current_options = None
        request_options = getattr(request, "options", None)
        if request_options:
            current_options = request_options.get(BodyInspectionHandlerOption.get_key(), None)
        if current_options:
            return current_options

        # Clear body per request
        self.options.request_body = None
        self.options.response_body = None
        return self.options
