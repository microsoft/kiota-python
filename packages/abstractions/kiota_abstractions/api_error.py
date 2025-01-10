from dataclasses import dataclass
from typing import Optional


@dataclass
class APIError(Exception):
    """The base class for all API errors."""

    message: Optional[str] = None
    response_status_code: Optional[int] = None
    response_headers: Optional[dict[str, str]] = None

    def __str__(self) -> str:
        error = getattr(self, "error", None)
        if error:
            return f"""
        APIError
        Code: {self.response_status_code}
        message: {self.message}
        error: {error}
        """
        return f"""
        APIError
        Code: {self.response_status_code}
        message: {self.message}
        """
