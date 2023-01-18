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
        """Callback method that is invoked when a response is received.
        Args:
            response (NativeResponseType): The type of the native response object.
            error_map (Optional[Dict[str, Optional[ParsableFactory]]]): the error dict to use
            in case of a failed request.
        Returns:
            Any: The native response object.
        """
        return response
