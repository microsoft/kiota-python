# ------------------------------------
# Copyright (c) Microsoft Corporation. All Rights Reserved.
# Licensed under the MIT License.
# See License in the project root for license information.
# ------------------------------------

from typing import Optional

import httpx

from .middleware import REQUEST_OPTIONS_KEY, BaseMiddleware
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
                response_content: Optional[bytes] = None
                # A consumed stream is inspectable only when HTTPX cached its content.
                if hasattr(response, "_content"):
                    response_content = response.content
                elif not response.is_stream_consumed and not response.is_closed:
                    num_bytes_downloaded = response.num_bytes_downloaded
                    raw_content = b"".join([chunk async for chunk in response.aiter_raw()])
                    self._restore_response_stream(response, raw_content, num_bytes_downloaded)
                    response_content = await response.aread()
                    self._restore_response_stream(response, raw_content, num_bytes_downloaded)
                if response_content:
                    current_options.response_body = response_content
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
        request_options = request.extensions.get(REQUEST_OPTIONS_KEY)
        if request_options:
            current_options = request_options.get(BodyInspectionHandlerOption.get_key(), None)
        if not current_options:
            current_options = self.options

        current_options._clear_captured_bodies()
        return current_options

    @staticmethod
    def _restore_response_stream(
        response: httpx.Response, content: bytes, num_bytes_downloaded: int
    ) -> None:
        # aread() caches decoded content and a stateful decoder; discard both when rewinding.
        if hasattr(response, "_content"):
            del response._content
        if hasattr(response, "_decoder"):
            del response._decoder
        response.stream = httpx.ByteStream(content)
        response.is_stream_consumed = False
        response.is_closed = False
        response._num_bytes_downloaded = num_bytes_downloaded
