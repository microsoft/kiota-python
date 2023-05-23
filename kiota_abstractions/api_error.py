from dataclasses import asdict, dataclass
from json import dumps
from typing import Dict, Optional


@dataclass
class APIError(Exception):
    """The base class for all API errors."""

    message: Optional[str] = None
    response_status_code: Optional[int] = None
    response_headers: Optional[Dict[str, str]] = None

    def __str__(self) -> str:
        return dumps(asdict(self), default=str)
