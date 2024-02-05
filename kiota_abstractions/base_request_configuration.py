# ------------------------------------
# Copyright (c) Microsoft Corporation. All Rights Reserved.
# Licensed under the MIT License.
# See License in the project root for license information.
# ------------------------------------
from dataclasses import dataclass
from typing import Dict, List, Optional
from warnings import warn

from .default_query_parameters import QueryParameters
from .headers_collection import HeadersCollection
from .request_option import RequestOption


@dataclass
class RequestConfiguration:
    """
    Configuration for the request such as headers, query parameters, and middleware options.
    """
    # Request headers
    headers: HeadersCollection = HeadersCollection()

    # Request options
    options: Optional[List[RequestOption]] = None

    query_parameters: Optional[QueryParameters] = None


@dataclass
class BaseRequestConfiguration:
    warn(
        "BaseRequestConfiguration is deprecated. Use RequestConfiguration class instead.",
        DeprecationWarning
    )
