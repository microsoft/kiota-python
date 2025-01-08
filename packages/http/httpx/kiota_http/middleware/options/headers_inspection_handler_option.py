# ------------------------------------
# Copyright (c) Microsoft Corporation. All Rights Reserved.
# Licensed under the MIT License.
# See License in the project root for license information.
# ------------------------------------
from kiota_abstractions.headers_collection import HeadersCollection
from kiota_abstractions.request_option import RequestOption


class HeadersInspectionHandlerOption(RequestOption):
    """Config options for the HeaderInspectionHandler"""

    HEADERS_INSPECTION_HANDLER_OPTION_KEY = "HeadersInspectionHandlerOption"

    def __init__(
        self,
        inspect_request_headers: bool = True,
        inspect_response_headers: bool = True,
        request_headers: HeadersCollection = HeadersCollection(),
        response_headers: HeadersCollection = HeadersCollection(),
    ) -> None:
        """Creates an instance of headers inspection handler option.

        Args:
            inspect_request_headers (bool, optional): whether the request headers
            should be inspected. Defaults to True.
            inspect_response_headers (bool, optional): whether the response headers
            should be inspected. Defaults to True.
        """
        self._inspect_request_headers = inspect_request_headers
        self._inspect_response_headers = inspect_response_headers
        self._request_headers = request_headers if request_headers else HeadersCollection()
        self._response_headers = response_headers if response_headers else HeadersCollection()

    @property
    def inspect_request_headers(self):
        """Whether the request headers should be inspected."""
        return self._inspect_request_headers

    @inspect_request_headers.setter
    def inspect_request_headers(self, value: bool):
        self._inspect_request_headers = value

    @property
    def inspect_response_headers(self):
        """Whether the response headers should be inspected."""
        return self._inspect_response_headers

    @inspect_response_headers.setter
    def inspect_response_headers(self, value: bool):
        self._inspect_response_headers = value

    @property
    def request_headers(self):
        """Gets the request headers to for the current request."""
        return self._request_headers

    @request_headers.setter
    def request_headers(self, value: HeadersCollection):
        self._request_headers = value

    @property
    def response_headers(self):
        """Gets the response headers to for the current request."""
        return self._response_headers

    @response_headers.setter
    def response_headers(self, value: HeadersCollection):
        self._response_headers = value

    @staticmethod
    def get_key() -> str:
        return HeadersInspectionHandlerOption.HEADERS_INSPECTION_HANDLER_OPTION_KEY
