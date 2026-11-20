from kiota_abstractions.request_option import RequestOption


class CompressionHandlerOption(RequestOption):
    """Config options for the CompressionHandler
    """

    COMPRESSION_HANDLER_OPTION_KEY = "CompressionHandlerOption"

    def __init__(self, enable_compression: bool = True) -> None:
        """Creates an instance of the compression handler option.

        Args:
            enable_compression (bool, optional): Whether to gzip request bodies.
            Defaults to True.
        """
        self._enable_compression = enable_compression

    @property
    def enable_compression(self) -> bool:
        """Whether request bodies are gzip compressed"""
        return self._enable_compression

    @enable_compression.setter
    def enable_compression(self, value: bool) -> None:
        self._enable_compression = value

    @staticmethod
    def get_key() -> str:
        return CompressionHandlerOption.COMPRESSION_HANDLER_OPTION_KEY
