import ssl
from typing import Optional

from opentelemetry import trace

import httpx

from .._version import VERSION
from ..observability_options import ObservabilityOptions

tracer = trace.get_tracer(ObservabilityOptions.get_tracer_instrumentation_name(), VERSION)

REQUEST_OPTIONS_KEY = "kiota_request_options"
PARENT_SPAN_KEY = "parent_span"


class MiddlewarePipeline():
    """MiddlewarePipeline, entry point of middleware
    The pipeline is implemented as a linked-list, read more about
    it here https://buffered.dev/middleware-python-requests/
    """

    def __init__(self, transport: httpx.AsyncBaseTransport) -> None:
        super().__init__()
        self._current_middleware: Optional[BaseMiddleware] = None
        self._first_middleware: Optional[BaseMiddleware] = None
        self._transport = transport

    def add_middleware(self, middleware: "BaseMiddleware") -> None:
        if self._current_middleware is None:
            self._first_middleware = middleware
        else:
            self._current_middleware.next = middleware
        self._current_middleware = middleware

    async def send(self, request: httpx.Request) -> httpx.Response:

        if self._first_middleware is not None:
            return await self._first_middleware.send(request, self._transport)
        # No middleware in pipeline, remove the request options and send the request
        if hasattr(request, "extensions") and isinstance(request.extensions, dict):
            options = request.extensions.get(REQUEST_OPTIONS_KEY)
            if options and (req_parent_span := options.get("parent_span", None)):
                request.extensions[PARENT_SPAN_KEY] = req_parent_span
            request.extensions.pop(REQUEST_OPTIONS_KEY, None)
        return await self._transport.handle_async_request(request)


class BaseMiddleware():
    """Base class for middleware. Handles moving a Request to the next middleware in the pipeline.
    If the current middleware is the last one in the pipeline, it makes a network request
    """

    def __init__(self) -> None:
        self.next: Optional[BaseMiddleware] = None
        self.parent_span: Optional[trace.Span] = None

    async def send(
        self, request: httpx.Request, transport: httpx.AsyncBaseTransport
    ) -> httpx.Response:
        if self.next is None:
            # Remove request options if there's no other middleware in the chain.
            if hasattr(request, "extensions") and isinstance(request.extensions, dict):
                options = request.extensions.get(REQUEST_OPTIONS_KEY)
                if options and (req_parent_span := options.get("parent_span", None)):
                    request.extensions[PARENT_SPAN_KEY] = req_parent_span
                request.extensions.pop(REQUEST_OPTIONS_KEY, None)
            response = await transport.handle_async_request(request)
            response.request = request
            return response
        return await self.next.send(request, transport)

    def _create_observability_span(self, request: httpx.Request, span_name: str) -> trace.Span:
        """Gets the parent_span from the request options and creates a new span.    
        If no parent_span is found in the request, uses the parent_span in the
        object. If parent_span is None, current context will be used."""
        options = None
        if hasattr(request, "extensions") and isinstance(request.extensions, dict):
            options = request.extensions.get(REQUEST_OPTIONS_KEY)
        parent_span = self.parent_span
        if options and (req_parent_span := options.get("parent_span", None)):
            parent_span = req_parent_span
            if hasattr(request, "extensions") and isinstance(request.extensions, dict):
                request.extensions[PARENT_SPAN_KEY] = req_parent_span
        elif hasattr(request, "extensions") and isinstance(
            request.extensions, dict
        ) and (req_parent_span := request.extensions.get(PARENT_SPAN_KEY)):
            parent_span = req_parent_span
        if parent_span is None:
            return tracer.start_span(span_name)
        return tracer.start_span(span_name, trace.set_span_in_context(parent_span))
