from typing import Optional

from kiota_abstractions.request_option import RequestOption


class UrlReplaceHandlerOption(RequestOption):
    """Config options for the UrlReplaceHandlerOption
    """

    URL_REPLACE_HANDLER_OPTION_KEY = "UrlReplaceHandlerOption"

    def __init__(
        self, enabled: bool = True, replacement_pairs: Optional[dict[str, str]] = None
    ) -> None:
        """Creates an instance of url replace option.

        Args:
            enabled (bool, optional): Whether to enable the url replace handler.
            Defaults to True.
            replacement_pairs (dict[str, str], optional): dictionary of values
            to replace. Defaults to {}.
        """
        self._enabled = enabled
        self._replacement_pairs = {} if replacement_pairs is None else replacement_pairs

    @property
    def is_enabled(self) -> bool:
        """Whether the url replace handler is enabled."""
        return self._enabled

    @is_enabled.setter
    def is_enabled(self, value: bool) -> None:
        self._enabled = value

    @property
    def replacement_pairs(self) -> dict[str, str]:
        """The key value pairs to replace"""
        return self._replacement_pairs

    @replacement_pairs.setter
    def replacement_pairs(self, value: dict[str, str]) -> None:
        self._replacement_pairs = value

    @staticmethod
    def get_key() -> str:
        return UrlReplaceHandlerOption.URL_REPLACE_HANDLER_OPTION_KEY
