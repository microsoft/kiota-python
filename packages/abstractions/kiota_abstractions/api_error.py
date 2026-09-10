from dataclasses import dataclass
from typing import Optional


@dataclass
class APIError(Exception):
    """The base class for all API errors."""

    message: Optional[str] = None
    response_status_code: Optional[int] = None
    response_headers: Optional[dict[str, str]] = None

    @property
    def primary_message(self) -> Optional[str]:
        """The message shown for this error. Generated error models override it with the
        message carried by the API's error payload."""
        return self.message

    def __str__(self) -> str:
        first_line = self.primary_message or type(self).__name__
        if self.response_status_code is not None:
            return f"{first_line} (status {self.response_status_code})"
        return first_line
