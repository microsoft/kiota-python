from typing import Dict
class APIError(Exception):
    """The base class for all API errors."""

    def __init__(self, message: str, headers: Dict[str, str], status_code: int) -> None:
        self._response_headers = headers
        self._response_status_code = status_code
        self._message = message
        super().__init__(self._message)

    @property
    def response_headers(self) -> Dict[str, str]:
        """The HTTP headers of the response that caused the error."""
        return self._response_headers

    @response_headers.setter
    def response_headers(self, value: Dict[str, str]) -> None:
        self._response_status_code = value
        
    @property
    def response_status_code(self) -> int:
        """The HTTP status code of the response that caused the error."""
        return self._response_status_code

    @response_status_code.setter
    def response_status_code(self, value: int) -> None:
        self._response_status_code = value
