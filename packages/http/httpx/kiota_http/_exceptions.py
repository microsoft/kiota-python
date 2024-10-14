"""Exceptions raised in Kiota HTTP."""


class KiotaHTTPXError(Exception):
    """Base class for Kiota HTTP exceptions."""


class BackingStoreError(KiotaHTTPXError):
    """Raised for the backing store."""


class DeserializationError(KiotaHTTPXError):
    """Raised for deserialization."""


class RequestError(KiotaHTTPXError):
    """Raised for request building errors."""


class ResponseError(KiotaHTTPXError):
    """Raised for response errors."""


class RedirectError(KiotaHTTPXError):
    """Raised when a redirect has errors."""
