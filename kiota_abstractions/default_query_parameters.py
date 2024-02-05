# ------------------------------------
# Copyright (c) Microsoft Corporation. All Rights Reserved.
# Licensed under the MIT License.
# See License in the project root for license information.
# ------------------------------------
from dataclasses import dataclass
from typing import List, Optional
from warnings import warn


@dataclass
class QueryParameters:
    """
    Default placeholder class for query parameters.
    """
    # Include count of items
    count: Optional[bool] = None

    # Expand related entities
    expand: Optional[List[str]] = None

    # Filter items by property values
    filter: Optional[str] = None

    # Order items by property values
    orderby: Optional[List[str]] = None

    # Select properties to be returned
    select: Optional[List[str]] = None

    # Skip the first n items
    skip: Optional[int] = None

    # Show only the first n items
    top: Optional[int] = None


@dataclass
class GetQueryParameters(QueryParameters):
    """
    Default placeholder class for query parameters.
    """
    warn("GetQueryParameters is deprecated. Use QueryParameters instead.", DeprecationWarning)
