import httpx

from .middleware import MiddlewarePipeline


class AsyncKiotaTransport(httpx.AsyncBaseTransport):
    """A custom transport that implements Kiota middleware functionality
    """

    def __init__(self, transport: httpx.AsyncBaseTransport, pipeline: MiddlewarePipeline) -> None:
        self.transport = transport
        self.pipeline = pipeline

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        if self.pipeline:
            response = await self.pipeline.send(request)
            return response

        response = await self.transport.handle_async_request(request)
        return response
