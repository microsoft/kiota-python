# ------------------------------------
# Copyright (c) Microsoft Corporation. All Rights Reserved.
# Licensed under the MIT License.
# See License in the project root for license information.
# ------------------------------------
from dataclasses import dataclass
from warnings import warn


@dataclass
class QueryParameters:
    """
    Default placeholder class for query parameters.
    """


@dataclass
class GetQueryParameters(QueryParameters):
    """
    Default placeholder class for query parameters.
    """
    warn("GetQueryParameters is deprecated. Use QueryParameters instead.", DeprecationWarning)
