# ------------------------------------
# Copyright (c) Microsoft Corporation. All Rights Reserved.
# Licensed under the MIT License.
# See License in the project root for license information.
# ------------------------------------

from kiota_abstractions.request_option import RequestOption

import httpx

from .middleware import BaseMiddleware
from .options import HeadersInspectionHandlerOption

HEADERS_INSPECTION_KEY = "com.microsoft.kiota.handler.headers_inspection.enable"


class HeadersInspectionHandler(BaseMiddleware):
    """The Headers Inspection Handler allows the developer to inspect the headers of the
    request and response.
    """

    def __init__(
        self,
        options: HeadersInspectionHandlerOption = HeadersInspectionHandlerOption(),
    ):
        """Create an instance of HeadersInspectionHandler

        Args:
            options (HeadersInspectionHandlerOption, optional): Default options to apply to the
            handler. Defaults to HeadersInspectionHandlerOption().
        """
        super().__init__()
        self.options = options

    async def send(
        self, request: httpx.Request, transport: httpx.AsyncBaseTransport
    ) -> httpx.Response:
        """To execute the current middleware

        Args:
            request (httpx.Request): The prepared request object
            transport(httpx.AsyncBaseTransport): The HTTP transport to use

        Returns:
            Response: The response object.
        """
        current_options = self._get_current_options(request)
        span = self._create_observability_span(request, "HeadersInspectionHandler_send")
        span.set_attribute(HEADERS_INSPECTION_KEY, True)
        span.end()

        if current_options and current_options.inspect_request_headers:
            for header in request.headers:
                current_options.request_headers.add(header, request.headers[header])
        response = await super().send(request, transport)
        if current_options and current_options.inspect_response_headers:
            for header in response.headers:
                current_options.response_headers.add(header, response.headers[header])
        return response

    def _get_current_options(self, request: httpx.Request) -> HeadersInspectionHandlerOption:
        """Returns the options to use for the request.Overrides default options if
        request options are passed.

        Args:
            request (httpx.Request): The prepared request object

        Returns:
            HeadersInspectionHandlerOption: The options to be used.
        """
        current_options = None
        request_options = getattr(request, "options", None)
        if request_options:
            current_options = request_options.get(  # type:ignore
                HeadersInspectionHandlerOption.get_key(), None
            )
        if current_options:
            return current_options

        # Clear headers per request
        self.options.request_headers.clear()
        self.options.response_headers.clear()
        return self.options
