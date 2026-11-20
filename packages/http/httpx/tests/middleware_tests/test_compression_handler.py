import gzip

import httpx
import pytest

from kiota_http.middleware import (
    REQUEST_OPTIONS_KEY,
    CompressionHandler,
    MiddlewarePipeline,
    RetryHandler,
)
from kiota_http.middleware.options import CompressionHandlerOption, RetryHandlerOption

BASE_URL = "https://graph.microsoft.com/v1.0/me/sendMail"
BODY = b'{"message": {"subject": "hello", "body": {"content": "' + b"a" * 200 + b'"}}}'


def recording_transport(status_codes=None):
    """Returns a mock transport that records each request it receives and answers
    with the given status codes in order (200 once they run out)."""
    status_codes = list(status_codes or [])
    received = []

    def handler(request):
        received.append({
            "headers": request.headers.copy(),
            "body": request.read(),
        })
        status = status_codes.pop(0) if status_codes else 200
        return httpx.Response(status, content=b"response body")

    return httpx.MockTransport(handler), received


def test_no_config():
    handler = CompressionHandler()
    assert handler.options.enable_compression is True
    assert handler.options.get_key() == "CompressionHandlerOption"


def test_custom_config():
    handler = CompressionHandler(options=CompressionHandlerOption(enable_compression=False))
    assert handler.options.enable_compression is False


@pytest.mark.asyncio
async def test_compresses_request_body():
    transport, received = recording_transport()
    request = httpx.Request("POST", BASE_URL, content=BODY)

    response = await CompressionHandler().send(request, transport)

    assert response.status_code == 200
    assert len(received) == 1
    sent = received[0]
    assert sent["headers"]["Content-Encoding"] == "gzip"
    assert sent["headers"]["Content-Length"] == str(len(sent["body"]))
    assert gzip.decompress(sent["body"]) == BODY
    assert len(sent["body"]) < len(BODY)
    # the original request is not modified
    assert "Content-Encoding" not in request.headers
    assert request.content == BODY


@pytest.mark.asyncio
async def test_compresses_streamed_request_body():

    async def body_stream():
        yield BODY[:10]
        yield BODY[10:]

    transport, received = recording_transport()
    request = httpx.Request("PUT", BASE_URL, content=body_stream())
    assert request.headers["Transfer-Encoding"] == "chunked"

    await CompressionHandler().send(request, transport)

    sent = received[0]
    assert "Transfer-Encoding" not in sent["headers"]
    assert sent["headers"]["Content-Length"] == str(len(sent["body"]))
    assert gzip.decompress(sent["body"]) == BODY


@pytest.mark.asyncio
async def test_does_not_compress_when_disabled():
    transport, received = recording_transport()
    request = httpx.Request("POST", BASE_URL, content=BODY)
    handler = CompressionHandler(options=CompressionHandlerOption(enable_compression=False))

    await handler.send(request, transport)

    assert "Content-Encoding" not in received[0]["headers"]
    assert received[0]["body"] == BODY


@pytest.mark.asyncio
async def test_request_option_overrides_handler_option():
    transport, received = recording_transport()
    option = CompressionHandlerOption(enable_compression=False)
    request = httpx.Request(
        "POST",
        BASE_URL,
        content=BODY,
        extensions={REQUEST_OPTIONS_KEY: {
            option.get_key(): option
        }}
    )

    await CompressionHandler().send(request, transport)

    assert "Content-Encoding" not in received[0]["headers"]
    assert received[0]["body"] == BODY

    transport, received = recording_transport()
    option = CompressionHandlerOption(enable_compression=True)
    request = httpx.Request(
        "POST",
        BASE_URL,
        content=BODY,
        extensions={REQUEST_OPTIONS_KEY: {
            option.get_key(): option
        }}
    )
    handler = CompressionHandler(options=CompressionHandlerOption(enable_compression=False))

    await handler.send(request, transport)

    assert received[0]["headers"]["Content-Encoding"] == "gzip"
    assert gzip.decompress(received[0]["body"]) == BODY


@pytest.mark.asyncio
async def test_does_not_compress_request_without_body():
    transport, received = recording_transport()
    request = httpx.Request("GET", BASE_URL)

    await CompressionHandler().send(request, transport)

    assert "Content-Encoding" not in received[0]["headers"]
    assert received[0]["body"] == b""


@pytest.mark.asyncio
async def test_does_not_compress_already_encoded_body():
    transport, received = recording_transport()
    encoded = gzip.compress(BODY)
    request = httpx.Request("POST", BASE_URL, content=encoded, headers={"Content-Encoding": "gzip"})

    await CompressionHandler().send(request, transport)

    assert received[0]["headers"]["Content-Encoding"] == "gzip"
    assert received[0]["body"] == encoded


@pytest.mark.asyncio
async def test_does_not_compress_body_with_bytes_content_range():
    transport, received = recording_transport()
    request = httpx.Request(
        "PUT", BASE_URL, content=BODY[:10], headers={"Content-Range": "bytes 0-9/20"}
    )

    await CompressionHandler().send(request, transport)

    assert "Content-Encoding" not in received[0]["headers"]
    assert received[0]["body"] == BODY[:10]


@pytest.mark.asyncio
async def test_sends_uncompressed_body_after_415():
    transport, received = recording_transport([415])
    request = httpx.Request("POST", BASE_URL, content=BODY)

    response = await CompressionHandler().send(request, transport)

    assert response.status_code == 200
    assert len(received) == 2
    assert received[0]["headers"]["Content-Encoding"] == "gzip"
    assert "Content-Encoding" not in received[1]["headers"]
    assert received[1]["headers"]["Content-Length"] == str(len(BODY))
    assert received[1]["body"] == BODY


@pytest.mark.asyncio
async def test_sends_uncompressed_body_only_once():
    transport, received = recording_transport([415, 415])
    request = httpx.Request("POST", BASE_URL, content=BODY)

    response = await CompressionHandler().send(request, transport)

    assert response.status_code == 415
    assert len(received) == 2


@pytest.mark.asyncio
async def test_does_not_resend_when_content_encoding_was_set_by_caller():
    transport, received = recording_transport([415])
    request = httpx.Request(
        "POST", BASE_URL, content=gzip.compress(BODY), headers={"Content-Encoding": "gzip"}
    )

    response = await CompressionHandler().send(request, transport)

    assert response.status_code == 415
    assert len(received) == 1


@pytest.mark.asyncio
async def test_retry_handler_resends_compressed_body():
    transport, received = recording_transport([503])
    retry_handler = RetryHandler(RetryHandlerOption(delay=0.0, max_retries=1))
    retry_handler.backoff_factor = 0.0
    retry_handler.backoff_max = 0
    pipeline = MiddlewarePipeline(transport)
    pipeline.add_middleware(CompressionHandler())
    pipeline.add_middleware(retry_handler)

    response = await pipeline.send(httpx.Request("POST", BASE_URL, content=BODY))

    assert response.status_code == 200
    assert len(received) == 2
    for sent in received:
        assert sent["headers"]["Content-Encoding"] == "gzip"
        assert gzip.decompress(sent["body"]) == BODY


@pytest.mark.asyncio
async def test_span_records_compression(span_exporter):
    transport, _ = recording_transport([415])
    request = httpx.Request("POST", BASE_URL, content=BODY)

    await CompressionHandler().send(request, transport)

    spans = span_exporter.get_finished_spans()
    assert [span.name for span in spans] == ["CompressionHandler_send"]
    attributes = spans[0].attributes
    assert attributes["com.microsoft.kiota.handler.compression.enable"] is True
    assert attributes["http.request.body.compressed"] is False
    assert attributes["http.request.body.size"] == len(BODY)
    assert attributes["http.response.status_code"] == 415


@pytest.mark.asyncio
async def test_null_request_raises():
    handler = CompressionHandler()
    with pytest.raises(TypeError, match="request cannot be null"):
        await handler.send(None, httpx.MockTransport(lambda req: httpx.Response(200)))
