from kiota_abstractions.request_option import RequestOption


class RedirectHandlerOption(RequestOption):

    # The default number of allowed redirects
    DEFAULT_MAX_REDIRECT = 5

    # The maximum allowed redirects
    MAX_MAX_REDIRECT = 20

    REDIRECT_HANDLER_OPTION_KEY = "RedirectHandlerOption"

    def __init__(
        self,
        max_redirect: int = DEFAULT_MAX_REDIRECT,
        should_redirect: bool = True,
        allow_redirect_on_scheme_change: bool = False
    ) -> None:

        if max_redirect > self.MAX_MAX_REDIRECT:
            raise ValueError("MaxLimitExceeded. Maximum value for max_redirect property exceeded")

        if max_redirect < 0:
            raise ValueError(
                "MaxLimitExceeded. Negative value for max_redirect property is invalid"
            )
        self._max_redirect = max_redirect
        self._should_redirect = should_redirect
        self._allow_redirect_on_scheme_change = allow_redirect_on_scheme_change

    @property
    def max_redirect(self):
        """The maximum number of redirects with a maximum value of 20.
        This defaults to 5 redirects."""
        return self._max_redirect

    @max_redirect.setter
    def max_redirect(self, value: int):
        if value > self.MAX_MAX_REDIRECT:
            raise ValueError("MaxLimitExceeded. Maximum value for max_redirect property exceeded")
        self._max_redirect = value

    @property
    def should_redirect(self):
        return self._should_redirect

    @should_redirect.setter
    def should_redirect(self, value: bool):
        self._should_redirect = value

    @property
    def allow_redirect_on_scheme_change(self):
        """A boolean value to determine if we redirects are allowed if the scheme changes
        (e.g. https to http). Defaults to false."""
        return self._allow_redirect_on_scheme_change

    @allow_redirect_on_scheme_change.setter
    def allow_redirect_on_scheme_change(self, value: bool):
        self._allow_redirect_on_scheme_change = value

    @staticmethod
    def get_key() -> str:
        return RedirectHandlerOption.REDIRECT_HANDLER_OPTION_KEY
