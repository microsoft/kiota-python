"""Test the BaseMiddleware class."""
from opentelemetry import trace

from kiota_http.middleware import BaseMiddleware


def test_next_is_none():
    """Ensure there is no next middleware."""
    middleware = BaseMiddleware()
    assert middleware.next is None

def test_span_created(request_info):
    """Ensures the current span is returned and the parent_span is not set."""
    middleware = BaseMiddleware()
    span = middleware._create_observability_span(request_info, "test_span_created")
    assert isinstance(span, trace.Span)
    assert middleware.parent_span is None
