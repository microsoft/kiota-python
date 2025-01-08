from kiota_abstractions.request_option import RequestOption

import httpx

from .middleware import BaseMiddleware
from .options import ParametersNameDecodingHandlerOption

PARAMETERS_NAME_DECODING_KEY = "com.microsoft.kiota.handler.parameters_name_decoding.enable"


class ParametersNameDecodingHandler(BaseMiddleware):

    def __init__(
        self,
        options: ParametersNameDecodingHandlerOption = ParametersNameDecodingHandlerOption(),
    ):
        """Create an instance of ParametersNameDecodingHandler

        Args:
            options (ParametersNameDecodingHandlerOption, optional): The parameters name
            decoding handler options value.
            Defaults to ParametersNameDecodingHandlerOption
        """
        super().__init__()
        self.options = options

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
        current_options = self._get_current_options(request)
        span = self._create_observability_span(request, "ParametersNameDecodingHandler_send")
        if current_options.enabled:
            span.set_attribute(PARAMETERS_NAME_DECODING_KEY, current_options.enabled)
        span.end()

        query_params = request.url.query.decode('utf-8')
        if all(
            [
                current_options,
                current_options.enabled,
                "%" in query_params,
                current_options.characters_to_decode,
            ]
        ):
            original_url: str = str(request.url)
            decoded_query_parameters_string = self.decode_uri_encoded_string(
                query_params, current_options.characters_to_decode
            )
            new_url = original_url.replace(query_params, decoded_query_parameters_string)
            request.url = httpx.URL(new_url)
        response = await super().send(request, transport)
        return response

    def _get_current_options(self, request: httpx.Request) -> ParametersNameDecodingHandlerOption:
        """Returns the options to use for the request.Overrides default options if
        request options are passed.

        Args:
            request (httpx.Request): The prepared request object

        Returns:
            ParametersNameDecodingHandlerOption: The options to used.
        """
        request_options = getattr(request, "options", None)
        if request_options:
            current_options = request_options.get(  # type:ignore
                ParametersNameDecodingHandlerOption.get_key(), self.options
            )
            return current_options
        return self.options

    def decode_uri_encoded_string(self, original: str, characters_to_decode: list[str]) -> str:
        """Decodes a uri encoded url string"""
        if not original or not characters_to_decode:
            return original
        symbols_to_replace = [
            (f"%{ord(x):X}", x) for x in characters_to_decode if f"%{ord(x):X}" in original
        ]

        encoded_parameter_values = [
            part.split('=')[0] for part in original.split('&') if '%' in part
        ]

        for parameter in encoded_parameter_values:
            for symbol_to_replace in symbols_to_replace:
                if symbol_to_replace[0] in parameter:
                    new_parameter = parameter.replace(symbol_to_replace[0], symbol_to_replace[1])
                    original = original.replace(parameter, new_parameter)

        return original
