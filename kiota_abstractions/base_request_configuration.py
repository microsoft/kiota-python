# ------------------------------------
# Copyright (c) Microsoft Corporation. All Rights Reserved.
# Licensed under the MIT License.
# See License in the project root for license information.
# ------------------------------------
from dataclasses import dataclass
from typing import Dict, List, Optional, Union

from .request_option import RequestOption


@dataclass
class BaseRequestConfiguration:
    """
    Configuration for the request such as headers, query parameters, and middleware options.
    """
    # Request headers
    headers: Optional[Dict[str, Union[str, List[str]]]] = None

    # Request options
    options: Optional[List[RequestOption]] = None
