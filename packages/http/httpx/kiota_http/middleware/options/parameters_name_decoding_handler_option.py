from kiota_abstractions.request_option import RequestOption


class ParametersNameDecodingHandlerOption(RequestOption):
    """Config options for the ParametersNameDecodingHandler
    """

    PARAMETERS_NAME_DECODING_HANDLER_OPTION_KEY = "ParametersNameDecodingHandlerOption"

    def __init__(
        self, enable: bool = True, characters_to_decode: list[str] = [".", "-", "~", "$"]
    ) -> None:
        """To create an instance of ParametersNameDecodingHandlerOptions

        Args:
            enable (bool, optional): - Whether to decode the specified characters in the
            request query parameters names. Defaults to True.
            characters_to_decode (list[str], optional):- The characters to decode.
            Defaults to [".", "-", "~", "$"].
        """
        self._enable = enable
        self._characters_to_decode = characters_to_decode

    @property
    def enabled(self):
        """Whether to decode the specified characters in the request query parameters"""
        return self._enable

    @enabled.setter
    def enabled(self, value: bool):
        self._enable = value

    @property
    def characters_to_decode(self):
        """The list of characters to decode in the request query parameters names before
        executing the request"""
        return self._characters_to_decode

    @characters_to_decode.setter
    def characters_to_decode(self, value: list[str]):
        self._characters_to_decode = value

    @staticmethod
    def get_key() -> str:
        return ParametersNameDecodingHandlerOption.PARAMETERS_NAME_DECODING_HANDLER_OPTION_KEY
