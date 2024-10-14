from kiota_abstractions.request_option import RequestOption

from kiota_http._version import VERSION


class UserAgentHandlerOption(RequestOption):
    """
    Configuration options for User Agent Handler.
    """

    USER_AGENT_HANDLER_OPTION_KEY = "AgentHandlerOption"

    def __init__(
        self,
        enabled: bool = True,
        product_name: str = "kiota-python",
        product_version: str = VERSION,
    ) -> None:
        self._enabled = enabled
        self._product_name = product_name
        self._product_version = product_version

    @property
    def is_enabled(self):
        """Returns True if the option is allowed."""
        return self._enabled

    @is_enabled.setter
    def is_enabled(self, value: bool):
        """Sets the option enabled value."""
        self._value = value

    @property
    def product_name(self):
        """Returns kiota-python if the name is not supplied."""
        return self._product_name

    @product_name.setter
    def product_name(self, value: str):
        """Sets the product name value."""
        if not value:
            raise ValueError("product_name cannot be empty.")
        self._product_name = value

    @property
    def product_version(self):
        """Returns VERSION valuerif the name is not supplied."""
        return self._product_version

    @product_version.setter
    def product_version(self, value: str):
        """Sets the product version value."""
        if not value:
            raise ValueError("product_version cannot be empty.")
        self._product_version = value

    @staticmethod
    def get_key() -> str:
        return UserAgentHandlerOption.USER_AGENT_HANDLER_OPTION_KEY
