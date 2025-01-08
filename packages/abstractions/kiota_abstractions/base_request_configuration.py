# ------------------------------------
# Copyright (c) Microsoft Corporation. All Rights Reserved.
# Licensed under the MIT License.
# See License in the project root for license information.
# ------------------------------------
from dataclasses import dataclass
from typing import Generic, Optional, TypeVar
from warnings import warn

from .headers_collection import HeadersCollection
from .request_option import RequestOption

QueryParameters = TypeVar('QueryParameters')


@dataclass
class RequestConfiguration(Generic[QueryParameters]):
    """
    Configuration for the request such as headers, query parameters, and middleware options.
    """
    # Request headers
    headers: HeadersCollection = HeadersCollection()
    # Request options
    options: Optional[list[RequestOption]] = None
    # Request query parameters
    query_parameters: Optional[QueryParameters] = None


@dataclass
class BaseRequestConfiguration(RequestConfiguration):

    def __post_init__(self):
        warn(
            "BaseRequestConfiguration is deprecated. Use RequestConfiguration class instead.",
            DeprecationWarning
        )
