from typing import Any, Callable, Dict, Optional, TypeVar, cast

from .serialization import Parsable, ParsableFactory

NativeResponseType = TypeVar("NativeResponseType")
ModelType = TypeVar("ModelType")


class NativeResponseHandler:
    """Default response handler to access the native response object.
    """

    @staticmethod
    async def handle_response_async(
            response: NativeResponseType) -> NativeResponseType:
        return response
