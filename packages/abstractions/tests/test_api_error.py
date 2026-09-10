from dataclasses import dataclass
from typing import Optional

from kiota_abstractions.api_error import APIError


@dataclass
class MainError:
    code: Optional[str] = None
    message: Optional[str] = None


@dataclass
class GeneratedError(APIError):
    """The shape kiota generates for an API's error model: an ``error`` payload and a
    ``primary_message`` property, and no ``message`` set by the deserializer."""

    error: Optional[MainError] = None

    @property
    def primary_message(self) -> str:
        if self.error is not None:
            return self.error.message or ""
        return ""


def test_str_is_the_message():
    assert str(APIError(message="boom")) == "boom"


def test_str_appends_the_status_code():
    assert str(APIError(message="boom", response_status_code=429)) == "boom (status 429)"


def test_str_without_any_message_names_the_class():
    assert str(APIError(response_status_code=502)) == "APIError (status 502)"


def test_str_of_a_generated_error_leads_with_the_primary_message():
    message = "Application is over its MailboxConcurrency limit."
    error = GeneratedError(
        response_status_code=429,
        error=MainError(code="ApplicationThrottled", message=message),
    )

    lines = str(error).splitlines()

    assert lines[0] == f"{message} (status 429)"
    assert lines[1].startswith("error: MainError(")
    assert "code='ApplicationThrottled'" in lines[1]


def test_str_never_starts_with_a_blank_line():
    for error in (APIError(), APIError(message="boom"), GeneratedError(error=MainError())):
        assert str(error).splitlines()[0].strip()
