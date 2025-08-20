"""Test the BaseMiddleware class."""
from opentelemetry import trace

from kiota_http.middleware import BaseMiddleware


def test_next_is_none():
    """Ensure there is no next middleware."""
    middleware = BaseMiddleware()
    assert middleware.next is None


def test_span_returned(request_info):
    """Ensures a span is returned and the parent_span is not set."""
    middleware = BaseMiddleware()
    span = middleware._create_observability_span(request_info, "test_span_returned")
    span.end()
    assert isinstance(span, trace.Span)
    assert middleware.parent_span is None


def test_span_created(request_info, otel_tracer):
    """Ensures the span returned does not end an outer context managed span"""
    with otel_tracer.start_as_current_span("outside-span") as outside_span:
        before_state = outside_span.is_recording()
        middleware = BaseMiddleware()
        span = middleware._create_observability_span(request_info, "test_span_created")
        span.end()
        after_state = outside_span.is_recording()
        assert(before_state == after_state)