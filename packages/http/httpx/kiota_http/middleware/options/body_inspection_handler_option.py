# ------------------------------------
# Copyright (c) Microsoft Corporation. All Rights Reserved.
# Licensed under the MIT License.
# See License in the project root for license information.
# ------------------------------------
from dataclasses import dataclass
from io import BytesIO
from typing import ClassVar, Optional

from kiota_abstractions.request_option import RequestOption


@dataclass(eq=False)
class BodyInspectionHandlerOption(RequestOption):
    """Config options for the BodyInspectionHandler.

    Args:
        inspect_request_body (bool, optional): Whether the request body
        should be inspected. Defaults to False. Note that this setting
        increases memory usage as the request body is copied in memory.
        inspect_response_body (bool, optional): Whether the response body
        should be inspected. Defaults to False. Note that this setting
        increases memory usage as the response body is copied in memory.
        request_body (Optional[bytes], optional): The inspected request body bytes.
        Defaults to None.
        response_body (Optional[bytes], optional): The inspected response body bytes.
        Defaults to None.
    """

    BODY_INSPECTION_HANDLER_OPTION_KEY: ClassVar[str] = "BodyInspectionHandlerOption"

    inspect_request_body: bool = False
    inspect_response_body: bool = False
    request_body: Optional[bytes] = None
    response_body: Optional[bytes] = None

    @staticmethod
    def get_key() -> str:
        return BodyInspectionHandlerOption.BODY_INSPECTION_HANDLER_OPTION_KEY

    def get_request_body(self) -> Optional[bytes]:
        """Gets the request body as bytes.

        Returns:
            Optional[bytes]: The request body bytes, or None if inspection was
            disabled or no body was present.
        """
        return self.request_body

    def get_response_body(self) -> Optional[bytes]:
        """Gets the response body as bytes.

        Returns:
            Optional[bytes]: The response body bytes, or None if inspection was
            disabled or no body was present.
        """
        return self.response_body

    def get_request_body_stream(self) -> Optional[BytesIO]:
        """Gets the request body as a seekable stream rewound to position 0.

        Callers are responsible for disposing/closing the stream. Note that this stream
        is a copy of the original request body, which has impact on memory usage.

        Returns:
            Optional[BytesIO]: A new BytesIO stream of the request body, or None if
            inspection was disabled or no body was present.
        """
        if self.request_body is not None:
            stream = BytesIO(self.request_body)
            stream.seek(0)
            return stream
        return None

    def get_response_body_stream(self) -> Optional[BytesIO]:
        """Gets the response body as a seekable stream rewound to position 0.

        Callers are responsible for disposing/closing the stream. Note that this stream
        is a copy of the original response body, which has impact on memory usage.

        Returns:
            Optional[BytesIO]: A new BytesIO stream of the response body, or None if
            inspection was disabled or no body was present.
        """
        if self.response_body is not None:
            stream = BytesIO(self.response_body)
            stream.seek(0)
            return stream
        return None

    @property
    def request_body_stream(self) -> Optional[BytesIO]:
        """Stream property for the request body rewound to position 0."""
        return self.get_request_body_stream()

    @property
    def response_body_stream(self) -> Optional[BytesIO]:
        """Stream property for the response body rewound to position 0."""
        return self.get_response_body_stream()
