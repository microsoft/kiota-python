"""Observability options for python http package."""
from kiota_abstractions.request_option import RequestOption


class ObservabilityOptions(RequestOption):
    """Defines the metrics, tracing and logging configurations."""
    OBSERVABILITY_OPTION_KEY = "ObservabilityOptionKey"

    def __init__(self, enabled: bool = True, include_euii_attributes: bool = True) -> None:
        """Initialize the observability options.

        Args:
            enabled(bool): whether to enable the ObservabilityOptions in the middleware chain.
            include_euii_attributes(bool): whether to include attributes that
                could contain EUII information likr URLS.
        """
        self._enabled = enabled
        self._include_euii_attributes = include_euii_attributes

    @property
    def enabled(self) -> bool:
        """Gets the enabled option value."""
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool):
        """sets whether to enable ObservabilityOptions in the middleware chain."""
        self._enabled = value

    @property
    def include_euii_attributes(self) -> bool:
        """Returns whether to include EUII attributes."""
        return self._include_euii_attributes

    @include_euii_attributes.setter
    def include_euii_attributes(self, value: bool) -> None:
        """Sets whether to include EUII attributes."""
        self._include_euii_attributes = value

    @staticmethod
    def get_key() -> str:
        """The middleware key name."""
        return ObservabilityOptions.OBSERVABILITY_OPTION_KEY

    @staticmethod
    def get_tracer_instrumentation_name() -> str:
        """Returns the instrumentation name used for tracing"""
        return "com.microsoft.com:microsoft-kiota-http-httpx"
