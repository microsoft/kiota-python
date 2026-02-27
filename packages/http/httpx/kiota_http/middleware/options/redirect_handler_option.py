from typing import Callable, Optional
from kiota_abstractions.request_option import RequestOption

import httpx

# Type alias for the scrub sensitive headers callback
ScrubSensitiveHeadersCallback = Callable[[httpx.Headers, httpx.URL, httpx.URL], None]


def default_scrub_sensitive_headers(
    headers: httpx.Headers, original_url: httpx.URL, new_url: httpx.URL
) -> None:
    """
    The default implementation for scrubbing sensitive headers during redirects.
    This method removes Authorization and Cookie headers when the host or scheme changes.
    Args:
        headers: The headers object to modify
        original_url: The original request URL
        new_url: The new redirect URL
    """
    if not headers or not original_url or not new_url:
        return

    # Remove Authorization and Cookie headers if the request's scheme or host changes
    is_different_host_or_scheme = (
        original_url.host != new_url.host or original_url.scheme != new_url.scheme
    )

    if is_different_host_or_scheme:
        headers.pop("Authorization", None)
        headers.pop("Cookie", None)

    # Note: Proxy-Authorization is not handled here as proxy configuration in httpx
    # is managed at the transport level and not accessible to middleware.
    # In environments where this matters, the proxy configuration should be managed
    # at the HTTP client level.


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
        allow_redirect_on_scheme_change: bool = False,
        scrub_sensitive_headers: Optional[ScrubSensitiveHeadersCallback] = None
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
        self._scrub_sensitive_headers = scrub_sensitive_headers or default_scrub_sensitive_headers

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

    @property
    def scrub_sensitive_headers(self) -> ScrubSensitiveHeadersCallback:
        """The callback for scrubbing sensitive headers during redirects.
        Defaults to default_scrub_sensitive_headers."""
        return self._scrub_sensitive_headers

    @scrub_sensitive_headers.setter
    def scrub_sensitive_headers(self, value: ScrubSensitiveHeadersCallback):
        self._scrub_sensitive_headers = value

    @staticmethod
    def get_key() -> str:
        return RedirectHandlerOption.REDIRECT_HANDLER_OPTION_KEY
