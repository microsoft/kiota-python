# ------------------------------------
# Copyright (c) Microsoft Corporation. All Rights Reserved.
# Licensed under the MIT License.
# See License in the project root for license information.
# ------------------------------------

from typing import Optional

import httpx

from .middleware import BaseMiddleware
from .options import BodyInspectionHandlerOption

BODY_INSPECTION_KEY = "com.microsoft.kiota.handler.bodyInspection.enable"


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
        if request is None:
            raise TypeError("request cannot be null")

        current_options = self._get_current_options(request)
        span = self._create_observability_span(request, "BodyInspectionHandler_send")
        try:
            span.set_attribute(BODY_INSPECTION_KEY, True)

            if current_options and current_options.inspect_request_body:
                content = await request.aread()
                if content:
                    current_options.request_body = content
                else:
                    current_options.request_body = None

            response = await super().send(request, transport)

            if current_options and current_options.inspect_response_body:
                if response.is_stream_consumed:
                    content = await response.aread()
                    raw_content = content
                else:
                    raw_content = b"".join([chunk async for chunk in response.aiter_raw()])
                    self._restore_response_stream(response, raw_content)
                    content = await response.aread()
                    self._restore_response_stream(response, raw_content)
                if content:
                    current_options.response_body = content
                else:
                    current_options.response_body = None

            return response
        finally:
            span.end()

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
        if not current_options:
            current_options = self.options

        # Clear body per request
        current_options.request_body = None
        current_options.response_body = None
        return current_options

    @staticmethod
    def _restore_response_stream(response: httpx.Response, content: bytes) -> None:
        response.stream = httpx.ByteStream(content)
        response.is_stream_consumed = False
        response.is_closed = False
