import gzip
from io import BytesIO

import pytest

import httpx
from kiota_http.middleware.body_inspection_handler import BodyInspectionHandler
from kiota_http.middleware.options.body_inspection_handler_option import BodyInspectionHandlerOption
from kiota_http.middleware.redirect_handler import RedirectHandler


def test_default_options():
    """Ensures default values are disabled and bodies are None."""
    options = BodyInspectionHandlerOption()
    assert not options.inspect_request_body
    assert not options.inspect_response_body
    assert options.request_body is None
    assert options.response_body is None
    assert options.get_request_body() is None
    assert options.get_response_body() is None
    assert options.get_request_body_stream() is None
    assert options.get_response_body_stream() is None
    assert options.request_body_stream is None
    assert options.response_body_stream is None


def test_custom_options():
    """Ensures that custom boolean flags are properly set."""
    options = BodyInspectionHandlerOption(
        inspect_request_body=True,
        inspect_response_body=True,
    )
    assert options.inspect_request_body
    assert options.inspect_response_body


def test_options_stream_helpers_and_rewinding():
    """Ensures stream accessors return seekable streams rewound to position 0."""
    options = BodyInspectionHandlerOption(
        request_body=b"request content",
        response_body=b"response content",
    )
    assert options.get_request_body() == b"request content"
    assert options.get_response_body() == b"response content"

    req_stream1 = options.get_request_body_stream()
    assert isinstance(req_stream1, BytesIO)
    assert req_stream1.tell() == 0
    assert req_stream1.read() == b"request content"

    # A subsequent call returns a new rewound stream, not an exhausted one
    req_stream2 = options.get_request_body_stream()
    assert isinstance(req_stream2, BytesIO)
    assert req_stream2.tell() == 0
    assert req_stream2.read() == b"request content"

    resp_stream1 = options.get_response_body_stream()
    assert isinstance(resp_stream1, BytesIO)
    assert resp_stream1.tell() == 0
    assert resp_stream1.read() == b"response content"

    resp_stream2 = options.response_body_stream
    assert isinstance(resp_stream2, BytesIO)
    assert resp_stream2.tell() == 0
    assert resp_stream2.read() == b"response content"


def test_handlers_do_not_share_options():
    """Two handlers without explicit options must not share option instances."""
    first = BodyInspectionHandler()
    second = BodyInspectionHandler()

    assert first.options is not second.options
    first.options.request_body = b"data"
    assert second.options.request_body is None


def test_body_inspection_handler_construction():
    """Ensures BodyInspectionHandler can be constructed."""
    handler = BodyInspectionHandler()
    assert handler is not None
    assert isinstance(handler.options, BodyInspectionHandlerOption)


@pytest.mark.asyncio
async def test_rejects_null_request():
    """Ensures a null request produces an intentional error."""
    handler = BodyInspectionHandler()

    with pytest.raises(TypeError, match="request cannot be null"):
        await handler.send(None, httpx.MockTransport(lambda _: httpx.Response(204)))


@pytest.mark.asyncio
async def test_observability_span_covers_full_send(monkeypatch):
    """Ensures telemetry covers the full body inspection handler execution."""
    attributes = {}
    events = []

    class RecordingSpan:

        def set_attribute(self, key, value):
            attributes[key] = value

        def end(self):
            events.append("span ended")

    async def response_body():
        events.append("response inspected")
        yield b"response body"

    def request_handler(request: httpx.Request):
        events.append("request sent")
        return httpx.Response(200, content=response_body())

    options = BodyInspectionHandlerOption(inspect_response_body=True)
    handler = BodyInspectionHandler(options=options)
    monkeypatch.setattr(handler, "_create_observability_span", lambda *_: RecordingSpan())

    request = httpx.Request("GET", "https://localhost")
    await handler.send(request, httpx.MockTransport(request_handler))

    assert attributes == {"com.microsoft.kiota.handler.bodyInspection.enable": True}
    assert events == ["request sent", "response inspected", "span ended"]


@pytest.mark.asyncio
async def test_observability_span_ends_when_send_raises(monkeypatch):
    """Ensures telemetry ends when the downstream transport raises."""
    events = []

    class RecordingSpan:

        def set_attribute(self, key, value):
            pass

        def end(self):
            events.append("span ended")

    def request_handler(request: httpx.Request):
        events.append("request sent")
        raise RuntimeError("transport failed")

    handler = BodyInspectionHandler()
    monkeypatch.setattr(handler, "_create_observability_span", lambda *_: RecordingSpan())

    request = httpx.Request("GET", "https://localhost")
    with pytest.raises(RuntimeError, match="transport failed"):
        await handler.send(request, httpx.MockTransport(request_handler))

    assert events == ["request sent", "span ended"]


@pytest.mark.asyncio
async def test_inspect_request_body():
    """Ensures request body is captured and downstream transport still receives it."""
    received = []

    def request_handler(request: httpx.Request):
        received.append(request.read())
        return httpx.Response(200, json={"message": "ok"})

    options = BodyInspectionHandlerOption(inspect_request_body=True)
    handler = BodyInspectionHandler(options=options)

    request = httpx.Request("POST", "https://localhost", content=b"hello request")
    mock_transport = httpx.MockTransport(request_handler)

    response = await handler.send(request, mock_transport)

    assert response.status_code == 200
    assert received == [b"hello request"]
    assert handler.options.request_body == b"hello request"
    assert handler.options.get_request_body() == b"hello request"
    assert handler.options.get_request_body_stream().read() == b"hello request"


@pytest.mark.asyncio
async def test_inspect_response_body():
    """Ensures response body is captured and caller can still consume the response."""

    def request_handler(request: httpx.Request):
        return httpx.Response(200, content=b'{"user": "alice"}')

    options = BodyInspectionHandlerOption(inspect_response_body=True)
    handler = BodyInspectionHandler(options=options)

    request = httpx.Request("GET", "https://localhost")
    mock_transport = httpx.MockTransport(request_handler)

    response = await handler.send(request, mock_transport)

    assert response.status_code == 200
    # Downstream caller can still read the response content
    assert response.content == b'{"user": "alice"}'
    assert response.json() == {"user": "alice"}
    # Handler option captured it
    assert handler.options.response_body == b'{"user": "alice"}'
    assert handler.options.get_response_body() == b'{"user": "alice"}'
    assert handler.options.get_response_body_stream().read() == b'{"user": "alice"}'


@pytest.mark.asyncio
async def test_inspect_both_request_and_response_body():
    """Ensures both request and response bodies can be inspected simultaneously."""

    def request_handler(request: httpx.Request):
        return httpx.Response(201, content=b'{"created": true}')

    options = BodyInspectionHandlerOption(
        inspect_request_body=True,
        inspect_response_body=True,
    )
    handler = BodyInspectionHandler(options=options)

    request = httpx.Request("POST", "https://localhost", content=b'{"name": "item"}')
    mock_transport = httpx.MockTransport(request_handler)

    response = await handler.send(request, mock_transport)

    assert response.status_code == 201
    assert handler.options.request_body == b'{"name": "item"}'
    assert handler.options.response_body == b'{"created": true}'


@pytest.mark.asyncio
async def test_disabled_inspection_does_not_capture():
    """Ensures bodies are not captured when inspection options are False."""

    def request_handler(request: httpx.Request):
        return httpx.Response(200, content=b'response content')

    handler = BodyInspectionHandler()

    request = httpx.Request("POST", "https://localhost", content=b'request content')
    mock_transport = httpx.MockTransport(request_handler)

    response = await handler.send(request, mock_transport)

    assert response.status_code == 200
    assert handler.options.request_body is None
    assert handler.options.response_body is None


@pytest.mark.asyncio
async def test_empty_bodies_returns_none():
    """Ensures empty request and response bodies result in None."""

    def request_handler(request: httpx.Request):
        return httpx.Response(204)

    options = BodyInspectionHandlerOption(
        inspect_request_body=True,
        inspect_response_body=True,
    )
    handler = BodyInspectionHandler(options=options)

    request = httpx.Request("GET", "https://localhost")
    mock_transport = httpx.MockTransport(request_handler)

    response = await handler.send(request, mock_transport)

    assert response.status_code == 204
    assert handler.options.request_body is None
    assert handler.options.response_body is None


@pytest.mark.asyncio
async def test_streaming_payloads_inspection():
    """Ensures streaming generators for request and response are preserved and inspected."""
    received = []

    async def req_gen():
        yield b"chunk1 "
        yield b"chunk2"

    async def resp_gen():
        yield b"stream1 "
        yield b"stream2"

    class RecordingTransport(httpx.AsyncBaseTransport):

        async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
            received.append(b"".join([chunk async for chunk in request.stream]))
            return httpx.Response(200, content=resp_gen())

    options = BodyInspectionHandlerOption(
        inspect_request_body=True,
        inspect_response_body=True,
    )
    handler = BodyInspectionHandler(options=options)

    request = httpx.Request("POST", "https://localhost", content=req_gen())
    response = await handler.send(request, RecordingTransport())

    assert response.status_code == 200
    assert received == [b"chunk1 chunk2"]
    assert handler.options.request_body == b"chunk1 chunk2"
    assert handler.options.response_body == b"stream1 stream2"
    assert response.content == b"stream1 stream2"


@pytest.mark.asyncio
async def test_inspected_streaming_response_remains_raw_iterable():
    """Ensures inspection does not consume the response stream returned to the caller."""

    async def resp_gen():
        yield b"stream1 "
        yield b"stream2"

    def request_handler(request: httpx.Request):
        return httpx.Response(200, content=resp_gen())

    options = BodyInspectionHandlerOption(inspect_response_body=True)
    handler = BodyInspectionHandler(options=options)

    response = await handler.send(
        httpx.Request("GET", "https://localhost"), httpx.MockTransport(request_handler)
    )
    raw_content = b"".join([chunk async for chunk in response.aiter_raw()])

    assert raw_content == b"stream1 stream2"
    assert options.response_body == b"stream1 stream2"


@pytest.mark.asyncio
async def test_inspected_buffered_response_keeps_consumed_raw_stream_state():
    """Ensures decoded buffered content is not exposed as replayable raw bytes."""
    compressed_content = gzip.compress(b"decoded response")

    def request_handler(request: httpx.Request):
        return httpx.Response(
            200,
            headers={"Content-Encoding": "gzip"},
            content=compressed_content,
        )

    options = BodyInspectionHandlerOption(inspect_response_body=True)
    handler = BodyInspectionHandler(options=options)

    response = await handler.send(
        httpx.Request("GET", "https://localhost"), httpx.MockTransport(request_handler)
    )

    assert options.response_body == b"decoded response"
    assert response.content == b"decoded response"
    assert response.is_stream_consumed
    assert response.is_closed
    with pytest.raises(httpx.StreamConsumed):
        b"".join([chunk async for chunk in response.aiter_raw()])


@pytest.mark.asyncio
async def test_per_request_options_override():
    """Ensures request-level options override handler-level options."""

    def request_handler(request: httpx.Request):
        return httpx.Response(200, content=b"response from server")

    # Handler defaults to inspection disabled
    handler = BodyInspectionHandler()

    per_request_option = BodyInspectionHandlerOption(
        inspect_request_body=True,
        inspect_response_body=True,
    )
    request = httpx.Request("POST", "https://localhost", content=b"request to server")
    setattr(request, "options", {BodyInspectionHandlerOption.get_key(): per_request_option})

    mock_transport = httpx.MockTransport(request_handler)
    response = await handler.send(request, mock_transport)

    assert response.status_code == 200
    # Captured on per_request_option
    assert per_request_option.request_body == b"request to server"
    assert per_request_option.response_body == b"response from server"
    # Handler options remained None
    assert handler.options.request_body is None
    assert handler.options.response_body is None


@pytest.mark.asyncio
async def test_per_request_options_apply_to_redirected_response():
    """Ensures redirect requests retain the original body inspection option."""

    def request_handler(request: httpx.Request):
        if request.url.path == "/redirected":
            return httpx.Response(200, content=b"final response")
        return httpx.Response(
            302,
            headers={"Location": "/redirected"},
            content=b"redirect response",
        )

    redirect_handler = RedirectHandler()
    redirect_handler.next = BodyInspectionHandler()
    per_request_option = BodyInspectionHandlerOption(inspect_response_body=True)
    request = httpx.Request("GET", "https://localhost")
    request.options = {BodyInspectionHandlerOption.get_key(): per_request_option}

    response = await redirect_handler.send(request, httpx.MockTransport(request_handler))

    assert response.status_code == 200
    assert per_request_option.response_body == b"final response"


@pytest.mark.asyncio
async def test_reused_per_request_option_clears_previous_bodies():
    """Ensures disabled inspection does not retain captures from a previous request."""

    def request_handler(request: httpx.Request):
        return httpx.Response(200, content=b"response body")

    handler = BodyInspectionHandler()
    option = BodyInspectionHandlerOption(
        inspect_request_body=True,
        inspect_response_body=True,
    )
    first_request = httpx.Request("POST", "https://localhost", content=b"request body")
    first_request.options = {BodyInspectionHandlerOption.get_key(): option}
    transport = httpx.MockTransport(request_handler)

    await handler.send(first_request, transport)
    assert option.request_body == b"request body"
    assert option.response_body == b"response body"

    option.inspect_request_body = False
    option.inspect_response_body = False
    second_request = httpx.Request("GET", "https://localhost")
    second_request.options = {BodyInspectionHandlerOption.get_key(): option}

    await handler.send(second_request, transport)

    assert option.request_body is None
    assert option.response_body is None


@pytest.mark.asyncio
async def test_handler_clears_body_on_subsequent_requests():
    """Ensures handler resets captured bodies across successive requests."""
    responses = [
        httpx.Response(200, content=b"response 1"),
        httpx.Response(200, content=b"response 2"),
        httpx.Response(204),
    ]

    def request_handler(request: httpx.Request):
        return responses.pop(0)

    options = BodyInspectionHandlerOption(
        inspect_request_body=True,
        inspect_response_body=True,
    )
    handler = BodyInspectionHandler(options=options)
    mock_transport = httpx.MockTransport(request_handler)

    # First request
    req1 = httpx.Request("POST", "https://localhost", content=b"req 1")
    await handler.send(req1, mock_transport)
    assert handler.options.request_body == b"req 1"
    assert handler.options.response_body == b"response 1"

    # Second request
    req2 = httpx.Request("POST", "https://localhost", content=b"req 2")
    await handler.send(req2, mock_transport)
    assert handler.options.request_body == b"req 2"
    assert handler.options.response_body == b"response 2"

    # Third request with no body
    req3 = httpx.Request("GET", "https://localhost")
    await handler.send(req3, mock_transport)
    assert handler.options.request_body is None
    assert handler.options.response_body is None
