from typing import Optional

from kiota_abstractions.request_option import RequestOption

import httpx

from .middleware import REQUEST_OPTIONS_KEY, BaseMiddleware
from .options import ParametersNameDecodingHandlerOption

PARAMETERS_NAME_DECODING_KEY = "com.microsoft.kiota.handler.parameters_name_decoding.enable"


class ParametersNameDecodingHandler(BaseMiddleware):

    def __init__(self, options: Optional[ParametersNameDecodingHandlerOption] = None) -> None:
        """Create an instance of ParametersNameDecodingHandler

        Args:
            options (ParametersNameDecodingHandlerOption, optional): The parameters name
            decoding handler options value. A new ParametersNameDecodingHandlerOption
            per handler when not provided.
        """
        super().__init__()
        self.options = options if options is not None else ParametersNameDecodingHandlerOption()

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
        if request is None:
            raise TypeError("request cannot be null")

        span = self._create_observability_span(request, "ParametersNameDecodingHandler_send")
        try:
            current_options = self._get_current_options(request)
            if current_options.enabled:
                span.set_attribute(PARAMETERS_NAME_DECODING_KEY, current_options.enabled)

            query_params = request.url.query.decode("utf-8")
            if all(
                [
                    current_options,
                    current_options.enabled,
                    "%" in query_params,
                    current_options.characters_to_decode,
                ]
            ):
                decoded_query_parameters_string = self.decode_uri_encoded_string(
                    query_params, current_options.characters_to_decode
                )
                request.url = request.url.copy_with(
                    query=decoded_query_parameters_string.encode("utf-8")
                )
            response = await super().send(request, transport)
            return response
        finally:
            span.end()

    def _get_current_options(self, request: httpx.Request) -> ParametersNameDecodingHandlerOption:
        """Returns the options to use for the request.Overrides default options if
        request options are passed.

        Args:
            request (httpx.Request): The prepared request object

        Returns:
            ParametersNameDecodingHandlerOption: The options to used.
        """
        request_options = request.extensions.get(REQUEST_OPTIONS_KEY)
        if request_options:
            current_options: ParametersNameDecodingHandlerOption = request_options.get(
                ParametersNameDecodingHandlerOption.get_key(), self.options
            )
            return current_options
        return self.options

    def decode_uri_encoded_string(self, original: str, characters_to_decode: list[str]) -> str:
        """Decodes a uri encoded query string, decoding characters only in parameter names."""
        if not original or not characters_to_decode:
            return original

        symbols_to_replace: list[tuple[str, str]] = []
        for x in characters_to_decode:
            code_upper = f"%{ord(x):02X}"
            code_lower = f"%{ord(x):02x}"
            symbols_to_replace.append((code_upper, x))
            if code_upper != code_lower:
                symbols_to_replace.append((code_lower, x))

        decoded_parts: list[str] = []
        for part in original.split("&"):
            if not part:
                decoded_parts.append(part)
                continue
            if "=" in part:
                param_name, param_value = part.split("=", 1)
                for code, symbol in symbols_to_replace:
                    if code in param_name:
                        param_name = param_name.replace(code, symbol)
                decoded_parts.append(f"{param_name}={param_value}")
            else:
                param_name = part
                for code, symbol in symbols_to_replace:
                    if code in param_name:
                        param_name = param_name.replace(code, symbol)
                decoded_parts.append(param_name)

        return "&".join(decoded_parts)
