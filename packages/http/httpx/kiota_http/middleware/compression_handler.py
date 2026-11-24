import asyncio
import gzip
from typing import Optional

from opentelemetry.semconv.attributes.http_attributes import HTTP_RESPONSE_STATUS_CODE

import httpx

from .middleware import REQUEST_OPTIONS_KEY, BaseMiddleware
from .options import CompressionHandlerOption

COMPRESSION_ENABLE_KEY = "com.microsoft.kiota.handler.compression.enable"
REQUEST_BODY_COMPRESSED_KEY = "http.request.body.compressed"
REQUEST_BODY_SIZE_KEY = "http.request.body.size"


class CompressionHandler(BaseMiddleware):
    """Middleware that gzip compresses request bodies.

    If the server answers a compressed request with 415 Unsupported Media Type, the
    request is sent once more with the original, uncompressed body.

    The handler is not part of the default middleware. Add it after RedirectHandler
    and before RetryHandler so 415 fallback stays within the current redirect hop.
    """

    CONTENT_ENCODING_HEADER = "Content-Encoding"
    CONTENT_RANGE_HEADER = "Content-Range"
    CONTENT_LENGTH_HEADER = "Content-Length"
    TRANSFER_ENCODING_HEADER = "Transfer-Encoding"
    UNSUPPORTED_MEDIA_TYPE = 415

    def __init__(self, options: Optional[CompressionHandlerOption] = None) -> None:
        """Create an instance of CompressionHandler

        Args:
            options (CompressionHandlerOption, optional): The compression options to
            use. A new CompressionHandlerOption is created when not provided.
        """
        super().__init__()
        self.options = options if options is not None else CompressionHandlerOption()

    async def send(
        self, request: httpx.Request, transport: httpx.AsyncBaseTransport
    ) -> httpx.Response:
        """To execute the current middleware

        Args:
            request (httpx.Request): The prepared request object
            transport(httpx.AsyncBaseTransport): The HTTP transport to use

        Returns:
            Response: The response object.
        """
        if request is None:
            raise TypeError("request cannot be null")
        _enable_span = self._create_observability_span(request, "CompressionHandler_send")
        try:
            current_options = self._get_current_options(request)
            _enable_span.set_attribute(COMPRESSION_ENABLE_KEY, current_options.enable_compression)
            if not current_options.enable_compression or not self._can_compress(request):
                return await super().send(request, transport)

            body = await request.aread()
            if not body:
                return await super().send(request, transport)

            # gzip is CPU bound, compress in a worker thread so large bodies do not
            # block the event loop
            compressed_body = await asyncio.to_thread(gzip.compress, body)
            compressed_request = self._build_compressed_request(request, compressed_body)
            _enable_span.set_attribute(REQUEST_BODY_COMPRESSED_KEY, True)
            _enable_span.set_attribute(REQUEST_BODY_SIZE_KEY, len(compressed_request.content))
            response = await super().send(compressed_request, transport)
            if response.status_code != self.UNSUPPORTED_MEDIA_TYPE:
                return response

            # The server does not accept compressed bodies, send the original request
            await response.aclose()
            _enable_span.set_attribute(HTTP_RESPONSE_STATUS_CODE, response.status_code)
            _enable_span.set_attribute(REQUEST_BODY_COMPRESSED_KEY, False)
            _enable_span.set_attribute(REQUEST_BODY_SIZE_KEY, len(body))
            return await super().send(request, transport)
        except Exception as exc:
            _enable_span.record_exception(exc)
            raise
        finally:
            _enable_span.end()

    def _get_current_options(self, request: httpx.Request) -> CompressionHandlerOption:
        """Returns the options to use for the request. The request options take
        precedence over the handler options.

        Args:
            request (httpx.Request): The prepared request object

        Returns:
            CompressionHandlerOption: The options to be used.
        """
        request_options = request.extensions.get(REQUEST_OPTIONS_KEY)
        if request_options:
            current_options: CompressionHandlerOption = request_options.get(
                CompressionHandlerOption.get_key(), self.options
            )
            return current_options
        return self.options

    def _can_compress(self, request: httpx.Request) -> bool:
        """Checks the request headers to decide whether the body can be compressed.
        Bodies that are already encoded, and partial bodies sent with a bytes
        Content-Range, are sent as they are.
        """
        if self.CONTENT_ENCODING_HEADER in request.headers:
            return False
        content_range = request.headers.get(self.CONTENT_RANGE_HEADER)
        if content_range is not None and "bytes" in content_range.lower():
            return False
        return True

    def _build_compressed_request(self, request: httpx.Request, body: bytes) -> httpx.Request:
        """Creates a copy of the request with a gzip compressed body.
        The original request is left untouched so it can be sent again uncompressed.
        """
        headers = request.headers.copy()
        headers.pop(self.TRANSFER_ENCODING_HEADER, None)
        headers[self.CONTENT_ENCODING_HEADER] = "gzip"
        headers[self.CONTENT_LENGTH_HEADER] = str(len(body))
        return httpx.Request(
            method=request.method,
            url=request.url,
            headers=headers,
            content=body,
            extensions=request.extensions.copy(),
        )
