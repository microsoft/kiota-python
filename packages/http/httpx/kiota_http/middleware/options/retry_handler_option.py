from kiota_abstractions.request_option import RequestOption


class RetryHandlerOption(RequestOption):
    """Options for the retry handler.

    Args:
        delay (float): base delay in seconds that the handler adds to every computed
            backoff, see ``RetryHandler.get_delay_time``. It is not a cap. Accepted range
            0 to ``MAX_DELAY``. Exposed as ``max_delay``. Defaults to ``DEFAULT_DELAY``.
        max_retries (int): number of retries after the first attempt, 0 to
            ``MAX_MAX_RETRIES``. Exposed as ``max_retry``.
        should_retry (bool): whether the handler retries at all.
        retry_unprocessed_mutations_only (bool): whether POST and PATCH requests are retried
            only after a response showing the server didn't process them. Defaults to False.
            POST and PATCH aren't idempotent, so resending one the server already processed
            can repeat its side effect, such as sending an email twice. A 504 can arrive after
            the server processed the request. When this is True, POST and PATCH requests are
            retried only after a 429 or 503 response, and a 504 is returned to the caller.
            This relies on the common service convention, followed by Microsoft Graph, that a
            429 or 503 response means the server didn't process the request. HTTP doesn't
            guarantee this, so a service that returns 429 or 503 after acting on a request can
            still see it repeated. PUT and DELETE also change state, but they're idempotent, so
            they aren't affected, and neither are other methods.
    """

    # Default maxRetries value
    DEFAULT_MAX_RETRIES: int = 3

    # Maximum number of retries values
    MAX_MAX_RETRIES: int = 10

    # Default delay value in seconds
    DEFAULT_DELAY: float = 3.0

    # Largest accepted delay value in seconds. The handler also skips the retry when the
    # computed delay is this value or more.
    MAX_DELAY: float = 180.0

    # Default value for should retry
    DEFAULT_SHOULD_RETRY: bool = True

    RETRY_HANDLER_OPTION_KEY = 'RetryHandlerOption'

    def __init__(
        self,
        delay: float = DEFAULT_DELAY,
        max_retries: int = DEFAULT_MAX_RETRIES,
        should_retry: bool = DEFAULT_SHOULD_RETRY,
        retry_unprocessed_mutations_only: bool = False
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
        self._retry_unprocessed_mutations_only: bool = retry_unprocessed_mutations_only

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

    @property
    def retry_unprocessed_mutations_only(self) -> bool:
        return self._retry_unprocessed_mutations_only

    @retry_unprocessed_mutations_only.setter
    def retry_unprocessed_mutations_only(self, value: bool) -> None:
        self._retry_unprocessed_mutations_only = value

    @staticmethod
    def get_key() -> str:
        return RetryHandlerOption.RETRY_HANDLER_OPTION_KEY
