from kiota_abstractions import RequestResponseLogger
from typing import Any, Dict
import logging

class HttpxRequestResponseLogger(RequestResponseLogger):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def log_request(self, request_data: Dict[str, Any]) -> None:
        self.logger.info(f"HTTP Request: {request_data}")

    def log_response(self, response_data: Dict[str, Any]) -> None:
        self.logger.info(f"HTTP Response: {response_data}")