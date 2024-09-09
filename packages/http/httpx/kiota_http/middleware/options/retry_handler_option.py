from kiota_abstractions.request_option import RequestOption


class RetryHandlerOption(RequestOption):
    """The retry request option class
    """

    # Default maxRetries value
    DEFAULT_MAX_RETRIES: int = 3

    # Maximum number of retries values
    MAX_MAX_RETRIES: int = 10

    # Default delay value in seconds
    DEFAULT_DELAY: float = 3.0

    # Default maximum delay value in seconds
    MAX_DELAY: float = 180.0

    # Default value for should retry
    DEFAULT_SHOULD_RETRY: bool = True

    RETRY_HANDLER_OPTION_KEY = 'RetryHandlerOption'

    def __init__(
        self,
        delay: float = DEFAULT_DELAY,
        max_retries: int = DEFAULT_MAX_RETRIES,
        should_retry: bool = DEFAULT_SHOULD_RETRY
    ) -> None:
        if delay > self.MAX_DELAY and max_retries > self.DEFAULT_MAX_RETRIES:
            raise ValueError(
                'MaxLimitExceeded. Delay and MaxRetries should not be more than'
                f'${self.MAX_DELAY} and ${self.MAX_MAX_RETRIES}'
            )
        if delay > self.MAX_DELAY:
            raise ValueError(f'MaxLimitExceeded. Delay should not be more than ${self.MAX_DELAY}')
        if max_retries > self.MAX_MAX_RETRIES:
            raise ValueError(
                f'MaxLimitExceeded. MaxRetries should not be more than ${self.MAX_MAX_RETRIES}'
            )
        if delay < 0 and max_retries < 0:
            raise ValueError('InvalidMinValue. Delay and MaxRetries should not be negative')
        if delay < 0:
            raise ValueError('InvalidMinValue. Delay should not be negative')
        if max_retries < 0:
            raise ValueError('InvalidMinValue. MaxRetries should not be negative')

        self._max_retry: int = min(max_retries, self.MAX_MAX_RETRIES)
        self._max_delay: float = min(delay, self.MAX_DELAY)
        self._should_retry: bool = should_retry

    @property
    def max_delay(self) -> float:
        return self._max_delay

    @max_delay.setter
    def max_delay(self, value: float) -> None:
        if value > self.MAX_DELAY:
            raise ValueError(f'MaxLimitExceeded. Delay should not be more than ${self.MAX_DELAY}')
        if value < 0:
            raise ValueError('InvalidMinValue. Delay should not be negative')
        self._max_delay = value

    @property
    def max_retry(self) -> int:
        return self._max_retry

    @max_retry.setter
    def max_retry(self, value: int) -> None:
        if value > self.MAX_MAX_RETRIES:
            raise ValueError(
                f'MaxLimitExceeded. MaxRetries should not be more than ${self.MAX_MAX_RETRIES}'
            )
        if value < 0:
            raise ValueError('InvalidMinValue. MaxRetries should not be negative')
        self._max_retry = value

    @property
    def should_retry(self) -> bool:
        return self._should_retry

    @should_retry.setter
    def should_retry(self, value: bool) -> None:
        self._should_retry = value

    @staticmethod
    def get_key():
        return RetryHandlerOption.RETRY_HANDLER_OPTION_KEY
