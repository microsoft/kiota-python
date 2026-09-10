# ------------------------------------
# Copyright (c) Microsoft Corporation. All Rights Reserved.
# Licensed under the MIT License.
# See License in the project root for license information.
# ------------------------------------
from dataclasses import dataclass, field
from typing import ClassVar

from kiota_abstractions.headers_collection import HeadersCollection
from kiota_abstractions.request_option import RequestOption


@dataclass(eq=False)
class HeadersInspectionHandlerOption(RequestOption):
    """Config options for the HeadersInspectionHandler.

    Args:
        inspect_request_headers (bool, optional): whether the request headers
        should be inspected. Defaults to True.
        inspect_response_headers (bool, optional): whether the response headers
        should be inspected. Defaults to True.
        request_headers (HeadersCollection, optional): collection that receives the
        request headers. A new one per option when not provided.
        response_headers (HeadersCollection, optional): collection that receives the
        response headers. A new one per option when not provided.
    """

    HEADERS_INSPECTION_HANDLER_OPTION_KEY: ClassVar[str] = "HeadersInspectionHandlerOption"

    inspect_request_headers: bool = True
    inspect_response_headers: bool = True
    request_headers: HeadersCollection = field(default_factory=HeadersCollection)
    response_headers: HeadersCollection = field(default_factory=HeadersCollection)

    @staticmethod
    def get_key() -> str:
        return HeadersInspectionHandlerOption.HEADERS_INSPECTION_HANDLER_OPTION_KEY
