from __future__ import annotations

from typing import Optional

from kiota_abstractions.request_option import RequestOption

import httpx
from kiota_http.middleware.options.user_agent_handler_option import UserAgentHandlerOption
from kiota_http.middleware.user_agent_handler import UserAgentHandler

from .middleware import (
    AsyncKiotaTransport,
    BaseMiddleware,
    HeadersInspectionHandler,
    MiddlewarePipeline,
    ParametersNameDecodingHandler,
    RedirectHandler,
    RetryHandler,
    UrlReplaceHandler,
)
from .middleware.options import (
    HeadersInspectionHandlerOption,
    ParametersNameDecodingHandlerOption,
    RedirectHandlerOption,
    RetryHandlerOption,
    UrlReplaceHandlerOption,
)

DEFAULT_CONNECTION_TIMEOUT: int = 30
DEFAULT_REQUEST_TIMEOUT: int = 100


class KiotaClientFactory:

    @staticmethod
    def get_default_client() -> httpx.AsyncClient:
        """Returns a native HTTP AsyncClient(httpx.AsyncClient) instance with default options

        Returns:
            httpx.AsyncClient
        """
        timeout = httpx.Timeout(DEFAULT_REQUEST_TIMEOUT, connect=DEFAULT_CONNECTION_TIMEOUT)
        return httpx.AsyncClient(timeout=timeout, http2=True)

    @staticmethod
    def create_with_default_middleware(
        client: Optional[httpx.AsyncClient] = None,
        options: Optional[dict[str, RequestOption]] = None
    ) -> httpx.AsyncClient:
        """Constructs native HTTP AsyncClient(httpx.AsyncClient) instances configured with
        a custom transport loaded with a default pipeline of middleware.

        Args:
            options (Optional[dict[str, RequestOption]]): The request options to use when
            instantiating default middleware. Defaults to dict[str, RequestOption]=None.

        Returns:
            httpx.AsyncClient: An instance of the AsyncClient object
        """

        kiota_async_client = KiotaClientFactory.get_default_client() if client is None else client
        middleware = KiotaClientFactory.get_default_middleware(options)

        return KiotaClientFactory._load_middleware_to_client(kiota_async_client, middleware)

    @staticmethod
    def create_with_custom_middleware(
        middleware: Optional[list[BaseMiddleware]],
        client: Optional[httpx.AsyncClient] = None,
    ) -> httpx.AsyncClient:
        """Constructs native HTTP AsyncClient(httpx.AsyncClient) instances configured with
        a custom pipeline of middleware.

        Args:
            middleware(list[BaseMiddleware]): Custom middleware list that will be used to create
            a middleware pipeline. The middleware should be arranged in the order in which they will
            modify the request.
        """
        kiota_async_client = KiotaClientFactory.get_default_client() if client is None else client
        return KiotaClientFactory._load_middleware_to_client(kiota_async_client, middleware)

    @staticmethod
    def get_default_middleware(options: Optional[dict[str, RequestOption]]) -> list[BaseMiddleware]:
        """
        Helper method that returns a list of default middleware instantiated with
        appropriate options
        """
        redirect_handler = RedirectHandler()
        retry_handler = RetryHandler()
        parameters_name_decoding_handler = ParametersNameDecodingHandler()
        url_replace_handler = UrlReplaceHandler()
        user_agent_handler = UserAgentHandler()
        headers_inspection_handler = HeadersInspectionHandler()

        if options:
            redirect_handler_options = options.get(RedirectHandlerOption.get_key())
            if redirect_handler_options and isinstance(
                redirect_handler_options, RedirectHandlerOption
            ):
                redirect_handler = RedirectHandler(options=redirect_handler_options)

            retry_handler_options = options.get(RetryHandlerOption.get_key())
            if retry_handler_options and isinstance(retry_handler_options, RetryHandlerOption):
                retry_handler = RetryHandler(options=retry_handler_options)

            parameters_name_decoding_handler_options = options.get(
                ParametersNameDecodingHandlerOption.get_key()
            )
            if parameters_name_decoding_handler_options and isinstance(
                parameters_name_decoding_handler_options, ParametersNameDecodingHandlerOption
            ):
                parameters_name_decoding_handler = ParametersNameDecodingHandler(
                    options=parameters_name_decoding_handler_options
                )

            url_replace_handler_options = options.get(UrlReplaceHandlerOption.get_key())
            if url_replace_handler_options and isinstance(
                url_replace_handler_options, UrlReplaceHandlerOption
            ):
                url_replace_handler = UrlReplaceHandler(options=url_replace_handler_options)

            user_agent_handler_options = options.get(UserAgentHandlerOption.get_key())
            if user_agent_handler_options and isinstance(
                user_agent_handler_options, UserAgentHandlerOption
            ):
                user_agent_handler = UserAgentHandler(options=user_agent_handler_options)

            headers_inspection_handler_options = options.get(
                HeadersInspectionHandlerOption.get_key()
            )
            if headers_inspection_handler_options and isinstance(
                headers_inspection_handler_options, HeadersInspectionHandlerOption
            ):
                headers_inspection_handler = HeadersInspectionHandler(
                    options=headers_inspection_handler_options
                )

        middleware = [
            redirect_handler, retry_handler, parameters_name_decoding_handler, url_replace_handler,
            user_agent_handler, headers_inspection_handler
        ]
        return middleware

    @staticmethod
    def create_middleware_pipeline(
        middleware: Optional[list[BaseMiddleware]], transport: httpx.AsyncBaseTransport
    ) -> MiddlewarePipeline:
        """
        Helper method that constructs a middleware_pipeline with the specified middleware
        """
        middleware_pipeline = MiddlewarePipeline(transport)
        if middleware:
            for ware in middleware:
                middleware_pipeline.add_middleware(ware)
        return middleware_pipeline

    @staticmethod
    def _load_middleware_to_client(
        client: httpx.AsyncClient, middleware: Optional[list[BaseMiddleware]]
    ) -> httpx.AsyncClient:
        current_transport = client._transport
        client._transport = KiotaClientFactory._replace_transport_with_custom_kiota_transport(
            current_transport, middleware
        )
        if client._mounts:
            mounts: dict = {}
            for pattern, transport in client._mounts.items():
                if transport is None:
                    mounts[pattern] = None
                else:
                    mounts[pattern
                           ] = KiotaClientFactory._replace_transport_with_custom_kiota_transport(
                               transport, middleware
                           )
            client._mounts = dict(sorted(mounts.items()))
        return client

    @staticmethod
    def _replace_transport_with_custom_kiota_transport(
        current_transport: httpx.AsyncBaseTransport, middleware: Optional[list[BaseMiddleware]]
    ) -> AsyncKiotaTransport:
        middleware_pipeline = KiotaClientFactory.create_middleware_pipeline(
            middleware, current_transport
        )
        new_transport = AsyncKiotaTransport(
            transport=current_transport, pipeline=middleware_pipeline
        )
        return new_transport
