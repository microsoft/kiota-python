class APIError(Exception):
    """The base class for all API errors."""

    def __init__(self, message: str, status_code: int) -> None:
        self._response_status_code = status_code
        self._message = message
        super().__init__(self._message)

    @property
    def response_status_code(self) -> int:
        """The HTTP status code of the response that caused the error."""
        return self._response_status_code

    @response_status_code.setter
    def response_status_code(self, value: int) -> None:
        self._response_status_code = value
