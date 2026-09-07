from dataclasses import dataclass
from typing import Optional


@dataclass
class APIError(Exception):
    """The base class for all API errors."""

    message: Optional[str] = None
    response_status_code: Optional[int] = None
    response_headers: Optional[dict[str, str]] = None

    def __str__(self) -> str:
        # Generated error models carry the server's message on ``primary_message`` and the
        # error payload on ``error``; the base class knows neither, so both are optional here.
        # The first line leads with the message so log lines and error titles show it.
        error = getattr(self, "error", None)
        message = getattr(self, "primary_message", None) or self.message or type(self).__name__
        details = []
        if self.response_status_code is not None:
            details.append(f"status {self.response_status_code}")
        code = getattr(error, "code", None)
        if code:
            details.append(f"code {code}")
        first_line = f"{message} ({', '.join(details)})" if details else str(message)
        if error:
            return f"{first_line}\nerror: {error}"
        return first_line
