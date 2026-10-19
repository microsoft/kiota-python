from typing import Optional

from kiota_abstractions.request_option import RequestOption
from opentelemetry.semconv.attributes.url_attributes import URL_FULL

import httpx

from .middleware import REQUEST_OPTIONS_KEY, BaseMiddleware
from .options import UrlReplaceHandlerOption


class UrlReplaceHandler(BaseMiddleware):

    def __init__(self, options: Optional[UrlReplaceHandlerOption] = None) -> None:
        """Create an instance of UrlReplaceHandler

        Args:
            options (UrlReplaceHandlerOption, optional): The url replacement
            options to pass to the handler. A new UrlReplaceHandlerOption
            per handler when not provided.
        """
        super().__init__()
        self.options = options if options is not None else UrlReplaceHandlerOption()

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
        _enable_span = self._create_observability_span(request, "UrlReplaceHandler_send")
        try:
            current_options = self._get_current_options(request)
            if current_options.is_enabled:
                _enable_span.set_attribute("com.microsoft.kiota.handler.url_replacer.enable", True)

                url_string: str = str(request.url)
                url_string = self.replace_url_segment(url_string, current_options)
                request.url = httpx.URL(url_string)
                _enable_span.set_attribute(URL_FULL, str(request.url))
            return await super().send(request, transport)
        finally:
            _enable_span.end()

    def _get_current_options(self, request: httpx.Request) -> UrlReplaceHandlerOption:
        """Returns the options to use for the request.Overries default options if
        request options are passed.

        Args:
            request (httpx.Request): The prepared request object

        Returns:
            UrlReplaceHandlerOption: The options to be used.
        """
        request_options = request.extensions.get(REQUEST_OPTIONS_KEY)
        if request_options:
            current_options: UrlReplaceHandlerOption = request_options.get(
                UrlReplaceHandlerOption.get_key(), self.options
            )
            return current_options
        return self.options

    def replace_url_segment(self, url_str: str, current_options: UrlReplaceHandlerOption) -> str:
        if all([current_options, current_options.is_enabled, current_options.replacement_pairs]):
            for k, v in current_options.replacement_pairs.items():
                url_str = url_str.replace(k, v, 1)
        return url_str
