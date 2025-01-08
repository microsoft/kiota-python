from typing import TYPE_CHECKING, Optional, Union

from kiota_abstractions.authentication import BaseBearerTokenAuthenticationProvider

from .azure_identity_access_token_provider import AzureIdentityAccessTokenProvider

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential
    from azure.core.credentials_async import AsyncTokenCredential


class AzureIdentityAuthenticationProvider(BaseBearerTokenAuthenticationProvider):

    # pylint: disable=too-many-positional-arguments
    def __init__(
        self,
        credentials: Union["TokenCredential", "AsyncTokenCredential"],
        options: Optional[dict] = None,
        scopes: list[str] = [],
        allowed_hosts: list[str] = [],
        is_cae_enabled: bool = True,
    ) -> None:
        """[summary]

        Args:
            credentials (Union["TokenCredential", "AsyncTokenCredential"]): The
                tokenCredential implementation to use for authentication.
            options (Optional[dict]): The options to use for authentication.
            scopes (list[str], optional): The scopes to use for authentication.
                Defaults to an empty list.
            allowed_hosts (set[str], optional): The allowed hosts to use for
                authentication.
        """
        super().__init__(
            AzureIdentityAccessTokenProvider(
                credentials, options, scopes, allowed_hosts, is_cae_enabled=is_cae_enabled
            )
        )
