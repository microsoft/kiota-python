"""Test the BaseMiddleware class."""
import httpx
import pytest
from opentelemetry import trace

from kiota_http.middleware import REQUEST_OPTIONS_KEY, BaseMiddleware, MiddlewarePipeline
from kiota_http.middleware import middleware as middleware_module


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


def test_span_without_parent_span_uses_the_current_span(span_exporter):
    middleware = BaseMiddleware()
    with middleware_module.tracer.start_as_current_span("outer"):
        middleware._create_observability_span(httpx.Request("GET", "https://example.com"), "inner").end()
    inner, outer = span_exporter.get_finished_spans()
    assert inner.parent.span_id == outer.context.span_id


@pytest.mark.asyncio
async def test_pipeline_without_middleware_sends_the_request():
    def request_handler(request: httpx.Request):
        return httpx.Response(200)

    request = httpx.Request("GET", "https://example.com", extensions={REQUEST_OPTIONS_KEY: {}})
    async with httpx.MockTransport(request_handler) as transport:
        response = await MiddlewarePipeline(transport).send(request)
    assert response.status_code == 200
    assert REQUEST_OPTIONS_KEY not in request.extensions

def test_parent_span_option_does_not_mutate_middleware_instance(span_exporter):
    middleware = BaseMiddleware()
    assert middleware.parent_span is None

    with middleware_module.tracer.start_as_current_span("parent-span-1") as span1:
        req1 = httpx.Request("GET", "https://example.com", extensions={REQUEST_OPTIONS_KEY: {"parent_span": span1}})
        child1 = middleware._create_observability_span(req1, "child1")
        child1.end()

    assert middleware.parent_span is None

    req2 = httpx.Request("GET", "https://example.com")
    child2 = middleware._create_observability_span(req2, "child2")
    child2.end()
    assert middleware.parent_span is None

    spans = span_exporter.get_finished_spans()
    child1_span = [s for s in spans if s.name == "child1"][0]
    parent1_span = [s for s in spans if s.name == "parent-span-1"][0]
    assert child1_span.parent.span_id == parent1_span.context.span_id
