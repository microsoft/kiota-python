from typing import Optional

from kiota_abstractions.request_option import RequestOption

from httpx import AsyncBaseTransport, Request, Response

from .middleware import REQUEST_OPTIONS_KEY, BaseMiddleware
from .options import UserAgentHandlerOption


class UserAgentHandler(BaseMiddleware):
    """
    Middleware handler for User Agent.
    """

    def __init__(self, options: Optional[UserAgentHandlerOption] = None) -> None:
        super().__init__()
        self.options = UserAgentHandlerOption() if options is None else options

    async def send(self, request: Request, transport: AsyncBaseTransport) -> Response:
        """
        Checks if the request has a User-Agent header and updates it if the
        platform config allows.
        """
        if request is None:
            raise TypeError("request cannot be null")
        current_options = self._get_current_options(request)
        _span = self._create_observability_span(request, "UserAgentHandler_send")
        try:
            if current_options and current_options.is_enabled:
                _span.set_attribute("com.microsoft.kiota.handler.useragent.enable", True)
                value = f"{current_options.product_name}/{current_options.product_version}"
                self._update_user_agent(request, value)
            return await super().send(request, transport)
        except Exception as exc:
            _span.record_exception(exc)
            raise
        finally:
            _span.end()

    def _get_current_options(self, request: Request) -> UserAgentHandlerOption:
        """Returns the options to use for the request.Overries default options if
        request options are passed.

        Args:
            request (httpx.Request): The prepared request object

        Returns:
            UserAgentHandlerOption: The options to be used.
        """
        request_options = request.extensions.get(REQUEST_OPTIONS_KEY)
        if request_options:
            current_options: UserAgentHandlerOption = request_options.get(
                UserAgentHandlerOption.get_key(), self.options
            )
            return current_options
        return self.options

    def _update_user_agent(self, request: Request, value: str) -> None:
        """Updates the values of the User-Agent header."""
        user_agent = request.headers.get("User-Agent", "")
        if not user_agent:
            request.headers.update({"User-Agent": value})
        else:
            if value not in user_agent:
                request.headers.update({"User-Agent": f"{user_agent} {value}"})
