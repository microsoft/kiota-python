import asyncio
import gzip
from dataclasses import dataclass
from typing import Optional
from weakref import ReferenceType, ref

from opentelemetry.semconv.attributes.http_attributes import HTTP_RESPONSE_STATUS_CODE
from opentelemetry.trace import Span

import httpx

from .middleware import REQUEST_OPTIONS_KEY, BaseMiddleware
from .options import CompressionHandlerOption
from .retry_handler import RETRY_ATTEMPT, _resume_hop_retries, _track_hop_retries

COMPRESSION_ENABLE_KEY = "com.microsoft.kiota.handler.compression.enable"
REQUEST_BODY_COMPRESSED_KEY = "http.request.body.compressed"
REQUEST_BODY_SIZE_KEY = "http.request.body.size"
_COMPRESSED_BODY_ATTR = "_kiota_compressed_body"


@dataclass(frozen=True)
class _CompressedBody:
    original: bytes
    compressed_stream: httpx.AsyncByteStream | httpx.SyncByteStream
    span: Span

    def matches(self, request: httpx.Request) -> bool:
        return (
            request.headers.get(CompressionHandler.CONTENT_ENCODING_HEADER) == "gzip"
            and request.stream is self.compressed_stream
        )


def _copy_context(source: httpx.Request, target: httpx.Request) -> None:
    if hasattr(source, "context"):
        target.context = source.context  # type: ignore[attr-defined]


def _carry_compressed_body(source: httpx.Request, target: httpx.Request) -> None:
    body = getattr(source, _COMPRESSED_BODY_ATTR, None)
    if body is not None and target.stream is source.stream:
        setattr(target, _COMPRESSED_BODY_ATTR, body)
        _track_hop_retries(target)


async def _uncompressed_retry(
    request: httpx.Request,
    response: httpx.Response,
    request_options: Optional[dict[str, object]],
    retry_attempt: Optional[str],
) -> Optional[httpx.Request]:
    if response.status_code != CompressionHandler.UNSUPPORTED_MEDIA_TYPE:
        return None
    body_ref: Optional[ReferenceType[_CompressedBody]]
    body_ref = getattr(request, _COMPRESSED_BODY_ATTR, None)
    body = body_ref() if body_ref is not None else None
    if body is None:
        return None
    try:
        actual_request = response.request
    except RuntimeError:
        return None
    if actual_request is not request or not body.matches(request):
        return None

    headers = request.headers.copy()
    headers.pop(CompressionHandler.CONTENT_ENCODING_HEADER, None)
    headers.pop(CompressionHandler.TRANSFER_ENCODING_HEADER, None)
    headers[CompressionHandler.CONTENT_LENGTH_HEADER] = str(len(body.original))
    if retry_attempt is None:
        headers.pop(RETRY_ATTEMPT, None)
    else:
        headers[RETRY_ATTEMPT] = retry_attempt
    extensions = request.extensions.copy()
    if request_options is not None:
        extensions[REQUEST_OPTIONS_KEY] = request_options
    replay = httpx.Request(
        request.method, request.url, headers=headers, content=body.original, extensions=extensions
    )
    _copy_context(request, replay)
    _resume_hop_retries(request, replay)
    await response.aclose()
    body.span.set_attribute(HTTP_RESPONSE_STATUS_CODE, response.status_code)
    body.span.set_attribute(REQUEST_BODY_COMPRESSED_KEY, False)
    body.span.set_attribute(REQUEST_BODY_SIZE_KEY, len(body.original))
    return replay


class CompressionHandler(BaseMiddleware):
    """Middleware that gzip compresses request bodies.

    If the server answers a compressed request with 415 Unsupported Media Type, the
    same hop is sent once more with the original, uncompressed body if the
    rejected compressed request can be identified.

    The handler is not part of the default middleware. Add it before RedirectHandler
    and RetryHandler to reuse the compressed body across redirects and retries.
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
            # Requests can outlive this invocation; don't retain the raw body on them.
            fallback_body = _CompressedBody(body, compressed_request.stream, _enable_span)
            setattr(compressed_request, _COMPRESSED_BODY_ATTR, ref(fallback_body))
            _track_hop_retries(compressed_request)
            retry_attempt = compressed_request.headers.get(RETRY_ATTEMPT)
            _enable_span.set_attribute(REQUEST_BODY_COMPRESSED_KEY, True)
            _enable_span.set_attribute(REQUEST_BODY_SIZE_KEY, len(compressed_request.content))
            response = await super().send(compressed_request, transport)
            replay = await _uncompressed_retry(
                compressed_request, response, request.extensions.get(REQUEST_OPTIONS_KEY),
                retry_attempt
            )
            return await super().send(replay, transport) if replay is not None else response
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
        compressed_request = httpx.Request(
            method=request.method,
            url=request.url,
            headers=headers,
            content=body,
            extensions=request.extensions.copy(),
        )
        _copy_context(request, compressed_request)
        return compressed_request
