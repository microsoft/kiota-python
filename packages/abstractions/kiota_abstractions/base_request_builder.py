# ------------------------------------
# Copyright (c) Microsoft Corporation. All Rights Reserved.
# Licensed under the MIT License.
# See License in the project root for license information.
# ------------------------------------
from typing import Any, Optional, Union

from .request_adapter import RequestAdapter
from .request_information import RequestInformation


class BaseRequestBuilder:
    """Base class for all request builders"""

    def __init__(
        self, request_adapter: RequestAdapter, url_template: str,
        path_parameters: Optional[Union[dict[str, Any], str]]
    ) -> None:
        """Initializes a new instance of the BaseRequestBuilder class."""
        if path_parameters is None:
            path_parameters = {}
        elif isinstance(path_parameters, str):
            path_parameters = {RequestInformation.RAW_URL_KEY: path_parameters}

        if request_adapter is None:
            raise TypeError("request_adapter cannot be null.")
        if url_template is None:
            raise TypeError("url_template cannot be null.")  # Empty string is allowed

        # Path parameters for the request
        self.path_parameters: dict[str, Any] = path_parameters
        # Url template to use to build the URL for the current request builder
        self.url_template: str = url_template
        # The request adapter to use to execute the requests.
        self.request_adapter = request_adapter
