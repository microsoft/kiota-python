from abc import ABC, abstractmethod
from typing import Any, Dict

class RequestResponseLogger(ABC):
    @abstractmethod
    def log_request(self, request_data: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    def log_response(self, response_data: Dict[str, Any]) -> None:
        pass