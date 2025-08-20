import ssl
from typing import Optional

from opentelemetry import trace

import httpx

from .._version import VERSION
from ..observability_options import ObservabilityOptions

tracer = trace.get_tracer(ObservabilityOptions.get_tracer_instrumentation_name(), VERSION)


class MiddlewarePipeline():
    """MiddlewarePipeline, entry point of middleware
    The pipeline is implemented as a linked-list, read more about
    it here https://buffered.dev/middleware-python-requests/
    """

    def __init__(self, transport: httpx.AsyncBaseTransport):
        super().__init__()
        self._current_middleware = None
        self._first_middleware = None
        self._transport = transport

    def add_middleware(self, middleware):
        if self._middleware_present():
            self._current_middleware.next = middleware
            self._current_middleware = middleware
        else:
            self._first_middleware = middleware
            self._current_middleware = self._first_middleware

    async def send(self, request):

        if self._middleware_present():
            return await self._first_middleware.send(request, self._transport)
        # No middleware in pipeline, delete request optoions from header and
        # send the request
        del request.headers['request_options']
        return await self._transport.handle_async_request(request)

    def _middleware_present(self):
        return self._current_middleware


class BaseMiddleware():
    """Base class for middleware. Handles moving a Request to the next middleware in the pipeline.
    If the current middleware is the last one in the pipeline, it makes a network request
    """

    def __init__(self):
        self.next = None
        self.parent_span = None

    async def send(self, request, transport):
        if self.next is None:
            # Remove request options if there's no other middleware in the chain.
            if hasattr(request, "options") and request.options:
                delattr(request, 'options')
            response = await transport.handle_async_request(request)
            response.request = request
            return response
        return await self.next.send(request, transport)

    def _create_observability_span(self, request, span_name: str) -> trace.Span:
        """Gets the parent_span from the request options and creates a new span.    
        If no parent_span is found in the request, uses the parent_span in the
        object. If parent_span is None, current context will be used."""
        _span = None
        if options := getattr(request, "options", None):
            if parent_span := options.get("parent_span", None):
                self.parent_span = parent_span
                _context = trace.set_span_in_context(parent_span)
                _span = tracer.start_span(span_name, _context)
        if _span is None:
            _context = trace.set_span_in_context(self.parent_span)
            _span = tracer.start_span(span_name, _context)
        return _span
