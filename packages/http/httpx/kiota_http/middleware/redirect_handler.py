import typing

from kiota_abstractions.request_option import RequestOption
from opentelemetry.semconv.attributes.http_attributes import HTTP_RESPONSE_STATUS_CODE

import httpx

from .._exceptions import RedirectError
from .middleware import BaseMiddleware
from .options import RedirectHandlerOption

REDIRECT_ENABLE_KEY = "com.microsoft.kiota.handler.redirect.enable"
REDIRECT_COUNT_KEY = "com.microsoft.kiota.handler.redirect.count"


class RedirectHandler(BaseMiddleware):
    """Middlware that allows us to define the redirect policy for all requests
    """

    DEFAULT_REDIRECT_STATUS_CODES: set[int] = {
        301,  # Moved Permanently
        302,  # Found
        303,  # See Other
        307,  # Temporary Redirect
        308,  # Moved Permanently
    }
    STATUS_CODE_SEE_OTHER: int = 303
    LOCATION_HEADER: str = "Location"
    AUTHORIZATION_HEADER: str = "Authorization"

    def __init__(self, options: RedirectHandlerOption = RedirectHandlerOption()) -> None:
        super().__init__()
        self.options = options
        self.redirect_on_status_codes: set[int] = self.DEFAULT_REDIRECT_STATUS_CODES

    def increment(self, response, max_redirect, history) -> bool:
        """Increment the redirect attempts for this request.
        Args
            response(httpx.Response): A httpx response object.
        Returns:
            bool: Whether further redirect attempts are remaining.
            False if exhausted; True if more redirect attempts available.
        """
        history.append(response.request)
        return max_redirect >= 0

    def get_redirect_location(self, response: httpx.Response) -> typing.Union[str, bool, None]:
        """Checks for redirect status code and gets redirect location.
        Args:
            response(httpx.Response): The Response object
        Returns:
            Union[str, bool, None]: Truthy redirect location string if we got a redirect status
            code and valid location. ``None`` if redirect status and no
            location. ``False`` if not a redirect status code.
        """
        if response.status_code in self.redirect_on_status_codes:
            return response.headers.get('location')
        return None

    async def send(
        self, request: httpx.Request, transport: httpx.AsyncBaseTransport
    ) -> httpx.Response:
        """Sends the http request object to the next middleware or redirects
        the request if necessary.
        """
        _enable_span = self._create_observability_span(request, "RedirectHandler_send")
        current_options = self._get_current_options(request)
        _enable_span.set_attribute(REDIRECT_ENABLE_KEY, True)
        _enable_span.end()

        max_redirect = current_options.max_redirect
        history: list[httpx.Request] = []

        while max_redirect >= 0:
            _redirect_span = self._create_observability_span(
                request, f"RedirectHandler_send - redirect {len(history)}"
            )
            response = await super().send(request, transport)
            _redirect_span.set_attribute(HTTP_RESPONSE_STATUS_CODE, response.status_code)
            redirect_location = self.get_redirect_location(response)

            if redirect_location and current_options.should_redirect:
                max_redirect -= 1
                if not self.increment(response, max_redirect, history[:]):
                    break
                _redirect_span.set_attribute(REDIRECT_COUNT_KEY, len(history))
                new_request = self._build_redirect_request(request, response, current_options)
                history.append(request)
                request = new_request
                await response.aclose()
                continue
            break
        response.history = history
        if max_redirect < 0:
            exc = RedirectError(f"Too many redirects. {response.history}")
            _redirect_span.record_exception(exc)
            _redirect_span.end()
            raise exc

        return response

    def _get_current_options(self, request: httpx.Request) -> RedirectHandlerOption:
        """Returns the options to use for the request.Overries default options if
        request options are passed.

        Args:
            request (httpx.Request): The prepared request object

        Returns:
            RedirectHandlerOption: The options to used.
        """
        request_options = getattr(request, "options", None)
        if request_options:
            current_options = request_options.get( # type:ignore
                RedirectHandlerOption.get_key(), self.options)
            return current_options
        return self.options

    def _build_redirect_request(
        self, request: httpx.Request, response: httpx.Response, options: RedirectHandlerOption
    ) -> httpx.Request:
        """
        Given a request and a redirect response, return a new request that
        should be used to effect the redirect.
        """
        method = self._redirect_method(request, response)
        url = self._redirect_url(request, response, options)
        headers = self._redirect_headers(request, url, method)
        stream = self._redirect_stream(request, method)
        new_request = httpx.Request(
            method=method,
            url=url,
            headers=headers,
            stream=stream,
            extensions=request.extensions,
        )
        if hasattr(request, "context"):
            new_request.context = request.context  #type: ignore
        new_request.options = {}  #type: ignore
        return new_request

    def _redirect_method(self, request: httpx.Request, response: httpx.Response) -> str:
        """
        When being redirected we may want to change the method of the request
        based on certain specs or browser behavior.
        """
        method = request.method

        # https://tools.ietf.org/html/rfc7231#section-6.4.4
        if response.status_code == self.STATUS_CODE_SEE_OTHER and method != "HEAD":
            method = "GET"

        # Do what the browsers do, despite standards...
        # Turn 302s into GETs.
        if response.status_code == 302 and method != "HEAD":
            method = "GET"

        # If a POST is responded to with a 301, turn it into a GET.
        # This bizarre behaviour is explained in 'requests' issue 1704.
        if response.status_code == 301 and method == "POST":
            method = "GET"

        return method

    def _redirect_url(
        self, request: httpx.Request, response: httpx.Response, options: RedirectHandlerOption
    ) -> httpx.URL:
        """
        Return the URL for the redirect to follow.
        """
        location = response.headers["Location"]

        try:
            url = httpx.URL(location)
        except Exception as exc:
            raise Exception(f"Invalid URL in location header: {exc}.")

        if (
            not url.is_relative_url and url.scheme != request.url.scheme
            and not options.allow_redirect_on_scheme_change
        ):
            raise Exception(
                "Redirects with changing schemes not allowed by default.\
                You can change this by modifying the allow_redirect_on_scheme_change\
                request option."
            )

        # Handle malformed 'Location' headers that are "absolute" form, have no host.
        # See: https://github.com/encode/httpx/issues/771
        if url.scheme and not url.host:
            url = url.copy_with(host=request.url.host)

        # Facilitate relative 'Location' headers, as allowed by RFC 7231.
        # (e.g. '/path/to/resource' instead of 'http://domain.tld/path/to/resource')
        if url.is_relative_url:
            url = request.url.join(url)

        # Attach previous fragment if needed (RFC 7231 7.1.2)
        if request.url.fragment and not url.fragment:
            url = url.copy_with(fragment=request.url.fragment)

        return url

    def _redirect_headers(
        self, request: httpx.Request, url: httpx.URL, method: str
    ) -> httpx.Headers:
        """
        Return the headers that should be used for the redirect request.
        """
        headers = httpx.Headers(request.headers)

        if not self._same_origin(url, request.url):
            if not self.is_https_redirect(request.url, url):
                # Strip Authorization headers when responses are redirected
                # away from the origin. (Except for direct HTTP to HTTPS redirects.)
                headers.pop("Authorization", None)

            # Update the Host header.
            headers["Host"] = url.netloc.decode("ascii")

        if method != request.method and method == "GET":
            # If we've switch to a 'GET' request, then strip any headers which
            # are only relevant to the request body.
            headers.pop("Content-Length", None)
            headers.pop("Transfer-Encoding", None)

        # We should use the client cookie store to determine any cookie header,
        # rather than whatever was on the original outgoing request.
        headers.pop("Cookie", None)

        return headers

    def _redirect_stream(
        self, request: httpx.Request, method: str
    ) -> typing.Optional[typing.Union[httpx.SyncByteStream, httpx.AsyncByteStream]]:
        """
        Return the body that should be used for the redirect request.
        """
        if method != request.method and method == "GET":
            return None

        return request.stream

    def _same_origin(self, url: httpx.URL, other: httpx.URL) -> bool:
        """
        Return 'True' if the given URLs share the same origin.
        """
        return (url.scheme == other.scheme and url.host == other.host)

    def port_or_default(self, url: httpx.URL) -> typing.Optional[int]:
        if url.port is not None:
            return url.port
        return {"http": 80, "https": 443}.get(url.scheme)

    def is_https_redirect(self, url: httpx.URL, location: httpx.URL) -> bool:
        """
        Return 'True' if 'location' is a HTTPS upgrade of 'url'
        """
        if url.host != location.host:
            return False

        return (url.scheme == "http" and location.scheme == "https")
