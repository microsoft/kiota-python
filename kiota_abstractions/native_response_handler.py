from typing import Dict, Optional, TypeVar

from .response_handler import ResponseHandler
from .serialization import ParsableFactory

NativeResponseType = TypeVar("NativeResponseType")
ModelType = TypeVar("ModelType")


class NativeResponseHandler(ResponseHandler):
    """Default response handler to access the native response object.
    """

    async def handle_response_async(
        self,
        response: NativeResponseType,
        error_map: Optional[Dict[str, Optional[ParsableFactory]]] = None
    ) -> NativeResponseType:
        return response
