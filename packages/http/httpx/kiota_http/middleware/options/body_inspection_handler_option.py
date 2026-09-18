# ------------------------------------
# Copyright (c) Microsoft Corporation. All Rights Reserved.
# Licensed under the MIT License.
# See License in the project root for license information.
# ------------------------------------
from contextvars import ContextVar
from io import BytesIO
from typing import ClassVar, Optional
from weakref import WeakKeyDictionary

from kiota_abstractions.request_option import RequestOption


class BodyInspectionHandlerOption(RequestOption):
    """Config options for the BodyInspectionHandler.

    Captured bodies are isolated by execution context so concurrent requests can
    safely share the same option instance.

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

    def __init__(
        self,
        inspect_request_body: bool = False,
        inspect_response_body: bool = False,
        request_body: Optional[bytes] = None,
        response_body: Optional[bytes] = None,
    ) -> None:
        self.inspect_request_body = inspect_request_body
        self.inspect_response_body = inspect_response_body
        self._default_request_body = request_body
        self._default_response_body = response_body

    @property
    def request_body(self) -> Optional[bytes]:
        """Gets the request body captured in the current execution context."""
        request_body, _ = self._get_captured_bodies()
        return request_body

    @request_body.setter
    def request_body(self, value: Optional[bytes]) -> None:
        _, response_body = self._get_captured_bodies()
        self._set_captured_bodies(value, response_body)

    @property
    def response_body(self) -> Optional[bytes]:
        """Gets the response body captured in the current execution context."""
        _, response_body = self._get_captured_bodies()
        return response_body

    @response_body.setter
    def response_body(self, value: Optional[bytes]) -> None:
        request_body, _ = self._get_captured_bodies()
        self._set_captured_bodies(request_body, value)

    def _get_captured_bodies(self) -> tuple[Optional[bytes], Optional[bytes]]:
        captures = _BODY_CAPTURES.get()
        if captures is not None:
            captured_bodies = captures.get(self)
            if captured_bodies is not None:
                return captured_bodies
        return self._default_request_body, self._default_response_body

    def _set_captured_bodies(
        self, request_body: Optional[bytes], response_body: Optional[bytes]
    ) -> None:
        current_captures = _BODY_CAPTURES.get()
        captures = (
            WeakKeyDictionary()
            if current_captures is None else WeakKeyDictionary(current_captures)
        )
        captures[self] = (request_body, response_body)
        _BODY_CAPTURES.set(captures)

    def _clear_captured_bodies(self) -> None:
        request_body, response_body = self._get_captured_bodies()
        if request_body is not None or response_body is not None:
            self._set_captured_bodies(None, None)

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


_BodyCapture = tuple[Optional[bytes], Optional[bytes]]
_BodyCaptureMap = WeakKeyDictionary[BodyInspectionHandlerOption, _BodyCapture]
_OptionalBodyCaptureMap = Optional[_BodyCaptureMap]
_BODY_CAPTURES: ContextVar[_OptionalBodyCaptureMap] = ContextVar(
    "kiota_body_inspection_captures", default=None
)
