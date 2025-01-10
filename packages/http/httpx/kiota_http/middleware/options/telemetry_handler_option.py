from collections.abc import Callable

from kiota_abstractions.request_option import RequestOption


class TelemetryHandlerOption(RequestOption):

    TELEMETRY_HANDLER_OPTION_KEY = 'TelemetryHandlerOption'

    def __init__(self, telemetry_configurator: Callable[[], None]) -> None:
        self._telemetry_configurator = telemetry_configurator

    @property
    def telemetry_configurator(self) -> Callable[[], None]:
        return self._telemetry_configurator

    @telemetry_configurator.setter
    def telemetry_configurator(self, value: Callable[[], None]) -> None:
        self._telemetry_configurator = value

    @staticmethod
    def get_key():
        return TelemetryHandlerOption.TELEMETRY_HANDLER_OPTION_KEY
