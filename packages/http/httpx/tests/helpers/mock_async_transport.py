import httpx

class MockTransport():
    async def handle_async_request(self, request):
        return httpx.Response(200, request=request, content=b'Hello World', headers={"Content-Type": "application/json", "test": "test_response_header"}) 