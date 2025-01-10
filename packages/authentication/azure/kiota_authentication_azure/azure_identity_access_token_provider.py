import base64
import inspect
from pickle import TRUE
from typing import Any, Optional, Union
from urllib.parse import urlparse

from kiota_abstractions.authentication import AccessTokenProvider, AllowedHostsValidator
from opentelemetry import trace

from azure.core.credentials import AccessToken, TokenCredential
from azure.core.credentials_async import AsyncTokenCredential

from ._exceptions import HTTPError
from ._version import VERSION

tracer = trace.get_tracer("microsoft-kiota-authentication-azure", VERSION)


class AzureIdentityAccessTokenProvider(AccessTokenProvider):
    """
    Access token provider that leverages the Azure Identity library to retrieve
    an access token.
    """

    IS_VALID_URL = "com.microsoft.kiota.authentication.is_url_valid"
    SCOPES = "com.microsoft.kiota.authentication.scopes"
    ADDITIONAL_CLAIMS_PROVIDED = "com.microsoft.kiota.authentication.additional_claims_provided"
    CLAIMS_KEY = "claims"
    LOCALHOST_STRINGS = {"localhost", "[::1]", "::1", "127.0.0.1"}

    # pylint: disable=too-many-positional-arguments
    def __init__(
        self,
        credentials: Union["TokenCredential", "AsyncTokenCredential"],
        options: Optional[dict],
        scopes: list[str] = [],
        allowed_hosts: list[str] = [],
        is_cae_enabled: bool = True,
    ) -> None:
        if not credentials:
            raise ValueError("Parameter credentials cannot be null")
        list_error = "should be an empty list or a list of strings"
        if not isinstance(scopes, list):
            raise TypeError(f"Scopes {list_error}")
        if not isinstance(allowed_hosts, list):
            raise TypeError(f"Allowed hosts {list_error}")

        self._credentials = credentials
        self._scopes = scopes
        self._options = options
        self._is_cae_enabled = is_cae_enabled
        self._allowed_hosts_validator = AllowedHostsValidator(allowed_hosts)

    async def get_authorization_token(
        self,
        uri: str,
        additional_authentication_context: dict[str, Any] = {},
    ) -> str:
        """This method is called by the BaseBearerTokenAuthenticationProvider class to get the
        access token.
        Args:
            uri (str): The target URI to get an access token for.
        Returns:
            str: The access token to use for the request.
        """
        with tracer.start_as_current_span("get_authorization_token") as span:
            if not self.get_allowed_hosts_validator().is_url_host_valid(uri):
                span.set_attribute(self.IS_VALID_URL, False)
                return ""

            parsed_url = urlparse(uri)
            if not all(
                [parsed_url.scheme, parsed_url.netloc]
            ) and parsed_url.scheme not in self.LOCALHOST_STRINGS:
                span.set_attribute(self.IS_VALID_URL, False)
                exc = HTTPError("Valid url scheme and host required")
                span.record_exception(exc)
                raise exc

            if parsed_url.scheme != "https" and (parsed_url.hostname not in self.LOCALHOST_STRINGS):
                span.set_attribute(self.IS_VALID_URL, False)
                exc = HTTPError("Only https is supported")
                span.record_exception(exc)
                raise exc

            span.set_attribute(self.IS_VALID_URL, TRUE)

            decoded_claim = None
            if all(
                [
                    additional_authentication_context,
                    self.CLAIMS_KEY in additional_authentication_context,
                    isinstance(additional_authentication_context.get(self.CLAIMS_KEY), str),
                ]
            ):
                decoded_bytes = base64.b64decode(additional_authentication_context[self.CLAIMS_KEY])
                decoded_claim = decoded_bytes.decode("utf-8")

            if not self._scopes:
                self._scopes = [f"{parsed_url.scheme}://{parsed_url.netloc}/.default"]
            span.set_attribute(self.SCOPES, ",".join(self._scopes))
            span.set_attribute(self.ADDITIONAL_CLAIMS_PROVIDED, bool(self._options))

            if self._options:
                result = self._credentials.get_token(
                    *self._scopes,
                    claims=decoded_claim,
                    enable_cae=self._is_cae_enabled,
                    **self._options
                )
            else:
                result = self._credentials.get_token(
                    *self._scopes, claims=decoded_claim, enable_cae=self._is_cae_enabled
                )

            if inspect.isawaitable(result):
                result = await result
                await self._credentials.close()  # type: ignore

            if result and isinstance(result, AccessToken):
                return result.token
            return ""

    def get_allowed_hosts_validator(self) -> AllowedHostsValidator:
        """Retrieves the allowed hosts validator.
        Returns:
            AllowedHostsValidator: The allowed hosts validator.
        """
        return self._allowed_hosts_validator
