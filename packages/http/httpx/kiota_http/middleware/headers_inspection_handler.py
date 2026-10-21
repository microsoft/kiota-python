# ------------------------------------
# Copyright (c) Microsoft Corporation. All Rights Reserved.
# Licensed under the MIT License.
# See License in the project root for license information.
# ------------------------------------

from typing import Optional

from kiota_abstractions.headers_collection import HeadersCollection
from kiota_abstractions.request_option import RequestOption

import httpx

from .middleware import REQUEST_OPTIONS_KEY, BaseMiddleware
from .options import HeadersInspectionHandlerOption

HEADERS_INSPECTION_KEY = "com.microsoft.kiota.handler.headers_inspection.enable"


class HeadersInspectionHandler(BaseMiddleware):
    """The Headers Inspection Handler allows the developer to inspect the headers of the
    request and response.
    """

    def __init__(
        self,
        options: Optional[HeadersInspectionHandlerOption] = None,
    ):
        """Create an instance of HeadersInspectionHandler

        Args:
            options (HeadersInspectionHandlerOption, optional): Default options to apply to the
            handler. A new HeadersInspectionHandlerOption per handler when not provided.
        """
        super().__init__()
        self.options = options if options is not None else HeadersInspectionHandlerOption()

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
        if request is None:
            raise TypeError("request cannot be null")

        current_options = self._get_current_options(request)
        span = self._create_observability_span(request, "HeadersInspectionHandler_send")
        try:
            span.set_attribute(HEADERS_INSPECTION_KEY, True)

            if current_options and current_options.inspect_request_headers:
                self._capture_headers(request.headers, current_options.request_headers)
            response = await super().send(request, transport)
            if current_options and current_options.inspect_response_headers:
                self._capture_headers(response.headers, current_options.response_headers)
            return response
        finally:
            span.end()

    def _capture_headers(
        self, source_headers: httpx.Headers, target_collection: HeadersCollection
    ) -> None:
        """Captures headers from httpx.Headers into a HeadersCollection.

        Headers belonging to SINGLE_VALUE_HEADERS preserve their combined string value,
        while other multi-valued headers preserve distinct list items.
        """
        for header in source_headers:
            if header.lower() in HeadersCollection.SINGLE_VALUE_HEADERS:
                target_collection.add(header, source_headers[header])
            else:
                target_collection.add(header, source_headers.get_list(header))

    def _get_current_options(self, request: httpx.Request) -> HeadersInspectionHandlerOption:
        """Returns the options to use for the request.Overrides default options if
        request options are passed.

        Args:
            request (httpx.Request): The prepared request object

        Returns:
            HeadersInspectionHandlerOption: The options to be used.
        """
        current_options: Optional[HeadersInspectionHandlerOption] = None
        request_options = request.extensions.get(REQUEST_OPTIONS_KEY)
        if request_options:
            current_options = request_options.get(HeadersInspectionHandlerOption.get_key(), None)
        if not current_options:
            current_options = self.options

        # Clear headers per request
        current_options.request_headers.clear()
        current_options.response_headers.clear()
        return current_options
