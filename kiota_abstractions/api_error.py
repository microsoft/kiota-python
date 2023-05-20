from typing import Dict, Optional

from pydantic.dataclasses import dataclass


@dataclass
class APIError(Exception):
    """The base class for all API errors."""

    error_message: Optional[str] = None
    # The HTTP headers of the response that caused the error.
    response_headers: Optional[Dict[str, str]] = None
    # The HTTP status code of the response that caused the error.
    response_status_code: Optional[int] = None
