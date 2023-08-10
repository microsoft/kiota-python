from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class APIError(Exception):
    """The base class for all API errors."""

    message: Optional[str] = None
    response_status_code: Optional[int] = None
    response_headers: Optional[Dict[str, str]] = None

    def __str__(self) -> str:
        return f"""APIError {self.response_status_code}: {self.message} {self.__getattribute__(
                'error')}"""
