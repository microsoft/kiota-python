"""HTTPX client request adapter."""
from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Optional, TypeVar, Union
from urllib import parse

from kiota_abstractions.api_client_builder import (
    enable_backing_store_for_parse_node_factory,
    enable_backing_store_for_serialization_writer_factory,
)
from kiota_abstractions.api_error import APIError
from kiota_abstractions.authentication import AuthenticationProvider
from kiota_abstractions.request_adapter import PrimitiveType, RequestAdapter, ResponseType
from kiota_abstractions.request_information import RequestInformation
from kiota_abstractions.serialization import (
    Parsable,
    ParsableFactory,
    ParseNode,
    ParseNodeFactory,
    ParseNodeFactoryRegistry,
    SerializationWriterFactory,
    SerializationWriterFactoryRegistry,
)
from kiota_abstractions.store import BackingStoreFactory, BackingStoreFactorySingleton
from opentelemetry import trace
from opentelemetry.semconv.attributes.http_attributes import (
    HTTP_REQUEST_METHOD,
    HTTP_RESPONSE_STATUS_CODE,
)
from opentelemetry.semconv.attributes.network_attributes import NETWORK_PROTOCOL_NAME
from opentelemetry.semconv.attributes.server_attributes import SERVER_ADDRESS
from opentelemetry.semconv.attributes.url_attributes import URL_FULL, URL_SCHEME

import httpx
from kiota_http._exceptions import (
    BackingStoreError,
    DeserializationError,
    RequestError,
    ResponseError,
)
from kiota_http.middleware.parameters_name_decoding_handler import ParametersNameDecodingHandler

from ._version import VERSION
from .kiota_client_factory import KiotaClientFactory
from .middleware import ParametersNameDecodingHandler
from .middleware.options import ParametersNameDecodingHandlerOption, ResponseHandlerOption
from .observability_options import ObservabilityOptions

ModelType = TypeVar("ModelType", bound=Parsable)

AUTHENTICATE_CHALLENGED_EVENT_KEY = "com.microsoft.kiota.authenticate_challenge_received"
RESPONSE_HANDLER_EVENT_INVOKED_KEY = "response_handler_invoked"
ERROR_MAPPING_FOUND_KEY = "com.microsoft.kiota.error.mapping_found"
ERROR_BODY_FOUND_KEY = "com.microsoft.kiota.error.body_found"
DESERIALIZED_MODEL_NAME_KEY = "com.microsoft.kiota.response.type"
REQUEST_IS_NULL = RequestError("Request info cannot be null")

tracer = trace.get_tracer(ObservabilityOptions.get_tracer_instrumentation_name(), VERSION)


class HttpxRequestAdapter(RequestAdapter):
    CLAIMS_KEY = "claims"
    BEARER_AUTHENTICATION_SCHEME = "Bearer"
    RESPONSE_AUTH_HEADER = "WWW-Authenticate"

    # pylint: disable=too-many-positional-arguments
    def __init__(
        self,
        authentication_provider: AuthenticationProvider,
        parse_node_factory: Optional[ParseNodeFactory] = None,
        serialization_writer_factory: Optional[SerializationWriterFactory] = None,
        http_client: Optional[httpx.AsyncClient] = None,
        base_url: Optional[str] = None,
        observability_options: Optional[ObservabilityOptions] = None,
    ) -> None:
        if not authentication_provider:
            raise TypeError("Authentication provider cannot be null")
        self._authentication_provider = authentication_provider
        if not parse_node_factory:
            parse_node_factory = ParseNodeFactoryRegistry()
        self._parse_node_factory = parse_node_factory
        if not serialization_writer_factory:
            serialization_writer_factory = SerializationWriterFactoryRegistry()
        self._serialization_writer_factory = serialization_writer_factory
        if not http_client:
            http_client = KiotaClientFactory.create_with_default_middleware()
        self._http_client: httpx.AsyncClient = http_client
        self._base_url: str = str(http_client.base_url) if http_client.base_url is not None else ""
        if not observability_options:
            observability_options = ObservabilityOptions()
        self.observability_options = observability_options

    @property
    def base_url(self) -> str:
        """Gets the base url for every request

        Returns:
            str: The base url
        """
        return self._base_url or str(
            self._http_client.base_url
        ) if self._http_client.base_url is not None else ""

    @base_url.setter
    def base_url(self, value: str) -> None:
        """Sets the base url for every request

        Args:
            value (str): The new base url
        """
        if value:
            self._base_url = value

    def get_serialization_writer_factory(self) -> SerializationWriterFactory:
        """Gets the serialization writer factory currently in use for the HTTP core service.
        Returns:
            SerializationWriterFactory: the serialization writer factory currently in use for the
            HTTP core service.
        """
        return self._serialization_writer_factory

    def get_response_content_type(self, response: httpx.Response) -> Optional[str]:
        header = response.headers.get("content-type")
        if not header:
            return None
        segments = header.lower().split(";")
        if not segments:
            return None
        return segments[0]

    def start_tracing_span(self, request_info: RequestInformation, method: str) -> trace.Span:
        """Creates an Opentelemetry tracer and starts the parent span.

        Args:
            request_info(RequestInformation): the request object.
            method(str): name of the invoker.

        Returns:
            The parent span.
        """

        uri_template = (request_info.url_template if request_info.url_template else "UNKNOWN")
        characters_to_decode_for_uri_template = ['$', '.', '-', '~']
        decoded_uri_template = ParametersNameDecodingHandler().decode_uri_encoded_string(
            uri_template, characters_to_decode_for_uri_template
        )
        parent_span_name = f"{method} - {decoded_uri_template}"

        span = tracer.start_span(parent_span_name)
        return span

    def _start_local_tracing_span(self, name: str, parent_span: trace.Span) -> trace.Span:
        """Helper function to start a span locally with the parent context."""
        _context = trace.set_span_in_context(parent_span)
        span = tracer.start_span(name, context=_context)
        return span

    async def send_async(
        self,
        request_info: RequestInformation,
        parsable_factory: ParsableFactory[ModelType],
        error_map: Optional[dict[str, type[ParsableFactory]]],
    ) -> Optional[ModelType]:
        """Excutes the HTTP request specified by the given RequestInformation and returns the
        deserialized response model.
        Args:
            request_info (RequestInformation): the request info to execute.
            parsable_factory (ParsableFactory): the class of the response model
            to deserialize the response into.
            error_map (dict[str, type[ParsableFactory]]): the error dict to use in
            case of a failed request.

        Returns:
            ModelType: the deserialized response model.
        """
        parent_span = self.start_tracing_span(request_info, "send_async")
        try:
            if not request_info:
                parent_span.record_exception(REQUEST_IS_NULL)
                raise REQUEST_IS_NULL

            response = await self.get_http_response_message(request_info, parent_span)

            response_handler = self.get_response_handler(request_info)
            if response_handler:
                parent_span.add_event(RESPONSE_HANDLER_EVENT_INVOKED_KEY)
                return await response_handler.handle_response_async(response, error_map)

            await self.throw_failed_responses(response, error_map, parent_span, parent_span)
            if self._should_return_none(response):
                return None
            root_node = await self.get_root_parse_node(response, parent_span, parent_span)
            if root_node is None:
                return None
            _deserialized_span = self._start_local_tracing_span("get_object_value", parent_span)
            value = root_node.get_object_value(parsable_factory)
            parent_span.set_attribute(DESERIALIZED_MODEL_NAME_KEY, value.__class__.__name__)
            _deserialized_span.end()
            return value  #type: ignore
        finally:
            parent_span.end()

    async def send_collection_async(
        self,
        request_info: RequestInformation,
        parsable_factory: ParsableFactory,
        error_map: Optional[dict[str, type[ParsableFactory]]],
    ) -> Optional[list[ModelType]]:
        """Excutes the HTTP request specified by the given RequestInformation and returns the
        deserialized response model collection.
        Args:
            request_info (RequestInformation): the request info to execute.
            parsable_factory (ParsableFactory): the class of the response model
            to deserialize the response into.
            error_map (dict[str, type[ParsableFactory]]): the error dict to use in
            case of a failed request.

        Returns:
            ModelType: the deserialized response model collection.
        """
        parent_span = self.start_tracing_span(request_info, "send_collection_async")
        try:
            if not request_info:
                parent_span.record_exception(REQUEST_IS_NULL)
                raise REQUEST_IS_NULL
            response = await self.get_http_response_message(request_info, parent_span)
            response_handler = self.get_response_handler(request_info)
            if response_handler:
                parent_span.add_event(RESPONSE_HANDLER_EVENT_INVOKED_KEY)
                return await response_handler.handle_response_async(response, error_map)

            await self.throw_failed_responses(response, error_map, parent_span, parent_span)
            if self._should_return_none(response):
                return None

            _deserialized_span = self._start_local_tracing_span(
                "get_collection_of_object_values", parent_span
            )
            root_node = await self.get_root_parse_node(response, parent_span, parent_span)
            if root_node:
                result: Optional[list[ModelType]
                                 ] = root_node.get_collection_of_object_values(parsable_factory)
                parent_span.set_attribute(DESERIALIZED_MODEL_NAME_KEY, result.__class__.__name__)
                _deserialized_span.end()
                return result
            return None
        finally:
            parent_span.end()

    async def send_collection_of_primitive_async(
        self,
        request_info: RequestInformation,
        response_type: type[PrimitiveType],
        error_map: Optional[dict[str, type[ParsableFactory]]],
    ) -> Optional[list[PrimitiveType]]:
        """Excutes the HTTP request specified by the given RequestInformation and returns the
        deserialized response model collection.
        Args:
            request_info (RequestInformation): the request info to execute.
            response_type (PrimitiveType): the class of the response model
            to deserialize the response into.
            error_map (dict[str, type[ParsableFactory]]): the error dict to use in
            case of a failed request.

        Returns:
            Optional[list[PrimitiveType]]: The deserialized primitive type collection.
        """
        parent_span = self.start_tracing_span(request_info, "send_collection_of_primitive_async")
        try:
            if not request_info:
                parent_span.record_exception(REQUEST_IS_NULL)
                raise REQUEST_IS_NULL

            response = await self.get_http_response_message(request_info, parent_span)
            response_handler = self.get_response_handler(request_info)
            if response_handler:
                parent_span.add_event(RESPONSE_HANDLER_EVENT_INVOKED_KEY)
                return await response_handler.handle_response_async(response, error_map)

            await self.throw_failed_responses(response, error_map, parent_span, parent_span)
            if self._should_return_none(response):
                return None

            _deserialized_span = self._start_local_tracing_span(
                "get_collection_of_primitive_values", parent_span
            )
            root_node = await self.get_root_parse_node(response, parent_span, parent_span)
            if root_node:
                values = root_node.get_collection_of_primitive_values(response_type)
                parent_span.set_attribute(DESERIALIZED_MODEL_NAME_KEY, values.__class__.__name__)
                _deserialized_span.end()
                return values  # type: ignore
            return None
        finally:
            parent_span.end()

    async def send_primitive_async(
        self,
        request_info: RequestInformation,
        response_type: str,
        error_map: Optional[dict[str, type[ParsableFactory]]],
    ) -> Optional[ResponseType]:
        """Excutes the HTTP request specified by the given RequestInformation and returns the
        deserialized primitive response model.
        Args:
            request_info (RequestInformation): the request info to execute.
            response_type (str): the class name of the response model to deserialize the
            response into.
            error_map (dict[str, type[ParsableFactory]]): the error dict to use in case
            of a failed request.

        Returns:
            Optional[ResponseType]: the deserialized primitive response model.
        """
        parent_span = self.start_tracing_span(request_info, "send_primitive_async")
        try:
            if not request_info:
                parent_span.record_exception(REQUEST_IS_NULL)
                raise REQUEST_IS_NULL

            response = await self.get_http_response_message(request_info, parent_span)

            response_handler = self.get_response_handler(request_info)
            if response_handler:
                parent_span.add_event(RESPONSE_HANDLER_EVENT_INVOKED_KEY)
                return await response_handler.handle_response_async(response, error_map)

            await self.throw_failed_responses(response, error_map, parent_span, parent_span)
            if self._should_return_none(response):
                return None

            if response_type == "bytes":
                return response.content  # type: ignore
            _deserialized_span = self._start_local_tracing_span("get_root_parse_node", parent_span)
            root_node = await self.get_root_parse_node(response, parent_span, parent_span)
            if not root_node:
                return None
            value: Optional[Union[str, int, float, bool, datetime, bytes]] = None
            if response_type == "str":
                value = root_node.get_str_value()
            if response_type == "int":
                value = root_node.get_int_value()
            if response_type == "float":
                value = root_node.get_float_value()
            if response_type == "bool":
                value = root_node.get_bool_value()
            if response_type == "datetime":
                value = root_node.get_datetime_value()
            if value is not None:
                parent_span.set_attribute(DESERIALIZED_MODEL_NAME_KEY, value.__class__.__name__)
                _deserialized_span.end()
                return value  # type: ignore

            exc = TypeError(f"Error handling the response, unexpected type {response_type!r}")
            parent_span.record_exception(exc)
            _deserialized_span.end()
            raise exc

        finally:
            parent_span.end()

    async def send_no_response_content_async(
        self, request_info: RequestInformation, error_map: Optional[dict[str,
                                                                         type[ParsableFactory]]]
    ) -> None:
        """Excutes the HTTP request specified by the given RequestInformation and returns the
        deserialized primitive response model.
        Args:
            request_info (RequestInformation):the request info to execute.
            error_map (dict[str, type[ParsableFactory]]): the error dict to use in case
            of a failed request.
        """
        parent_span = self.start_tracing_span(request_info, "send_no_response_content_async")
        try:
            if not request_info:
                parent_span.record_exception(REQUEST_IS_NULL)
                raise REQUEST_IS_NULL

            response = await self.get_http_response_message(request_info, parent_span)
            response_handler = self.get_response_handler(request_info)
            if response_handler:
                parent_span.add_event(RESPONSE_HANDLER_EVENT_INVOKED_KEY)
                return await response_handler.handle_response_async(response, error_map)

            await self.throw_failed_responses(response, error_map, parent_span, parent_span)
        finally:
            parent_span.end()

    def enable_backing_store(self, backing_store_factory: Optional[BackingStoreFactory]) -> None:
        """Enables the backing store proxies for the SerializationWriters and ParseNodes in use.
        Args:
            backing_store_factory (Optional[BackingStoreFactory]): the backing store factory to use.
        """
        self._parse_node_factory = enable_backing_store_for_parse_node_factory(
            self._parse_node_factory
        )
        self._serialization_writer_factory = (
            enable_backing_store_for_serialization_writer_factory(
                self._serialization_writer_factory
            )
        )
        if not any([self._serialization_writer_factory, self._parse_node_factory]):
            raise BackingStoreError("Unable to enable backing store")
        if backing_store_factory:
            BackingStoreFactorySingleton(backing_store_factory=backing_store_factory)

    async def get_root_parse_node(
        self,
        response: httpx.Response,
        parent_span: trace.Span,
        attribute_span: trace.Span,
    ) -> Optional[ParseNode]:
        span = self._start_local_tracing_span("get_root_parse_node", parent_span)

        try:
            payload = response.content
            response_content_type = self.get_response_content_type(response)
            if not response_content_type:
                return None
            return self._parse_node_factory.get_root_parse_node(response_content_type, payload)
        finally:
            span.end()

    def _should_return_none(self, response: httpx.Response) -> bool:
        """Helper function to check if the response should return None.

        Conditions:
            - The response status code is 204 or 304
            - the response content is empty.
            - The response status code is 301 or 302 and the location header is not present.

        Returns:
            bool: True if the response should return None, False otherwise.
        """
        return response.status_code == 204 or response.status_code == 304 or not bool(
            response.content
        ) or (not response.headers.get("location") and response.status_code in [301, 302])

    def _is_redirect_missing_location(
        self, response: httpx.Response, parent_span: trace.Span, attribute_span: trace.Span
    ) -> bool:
        if response.is_redirect:
            if response.has_redirect_location:
                return False
            # Raise a more specific error if the server returned a redirect status code
            # without a location header
            attribute_span.set_status(trace.StatusCode.ERROR)
            _throw_failed_resp_span = self._start_local_tracing_span(
                "throw_failed_responses", parent_span
            )
            _throw_failed_resp_span.set_attribute("status", response.status_code)
            exc = APIError(
                f"The server returned a redirect status code {response.status_code}"
                " without a location header",
                response.status_code,
                response.headers,  # type: ignore
            )
            _throw_failed_resp_span.set_status(trace.StatusCode.ERROR, str(exc))
            attribute_span.record_exception(exc)
            _throw_failed_resp_span.end()
            raise exc
        return True

    async def _get_error_from_response(
        self,
        response: httpx.Response,
        error_map: dict[str, type[ParsableFactory]],
        response_status_code_str: str,
        response_status_code: int,
        attribute_span: trace.Span,
        _throw_failed_resp_span: trace.Span,
    ) -> object:
        error_class = None
        if response_status_code_str in error_map:  # Error Code 400 - <= 599
            error_class = error_map[response_status_code_str]
        elif 400 <= response_status_code < 500 and "4XX" in error_map:  # Error code 4XX
            error_class = error_map["4XX"]
        elif 500 <= response_status_code < 600 and "5XX" in error_map:  # Error code 5XX
            error_class = error_map["5XX"]
        elif "XXX" in error_map:  # Blanket case
            error_class = error_map["XXX"]

        root_node = await self.get_root_parse_node(
            response, _throw_failed_resp_span, _throw_failed_resp_span
        )
        attribute_span.set_attribute(ERROR_BODY_FOUND_KEY, bool(root_node))

        _get_obj_ctx = trace.set_span_in_context(_throw_failed_resp_span)
        _get_obj_span = tracer.start_span("get_object_value", context=_get_obj_ctx)

        if not root_node:
            return None
        error = None
        if error_class:
            error = root_node.get_object_value(error_class)
            _get_obj_span.end()
        return error

    async def throw_failed_responses(
        self,
        response: httpx.Response,
        error_map: Optional[dict[str, type[ParsableFactory]]],
        parent_span: trace.Span,
        attribute_span: trace.Span,
    ) -> None:
        if response.is_success or response.status_code == 304:
            return
        if self._is_redirect_missing_location(response, parent_span, attribute_span) is False:
            return
        try:
            attribute_span.set_status(trace.StatusCode.ERROR)

            _throw_failed_resp_span = self._start_local_tracing_span(
                "throw_failed_responses", parent_span
            )

            response_status_code = response.status_code
            response_status_code_str = str(response_status_code)
            response_headers = response.headers

            _throw_failed_resp_span.set_attribute("status", response_status_code)
            _throw_failed_resp_span.set_attribute(ERROR_MAPPING_FOUND_KEY, bool(error_map))
            if not error_map:
                exc = APIError(
                    "The server returned an unexpected status code and no error class is registered"
                    f" for this code {response_status_code}",
                    response_status_code,
                    response_headers,  # type: ignore
                )
                # set this or ignore as description in set_status?
                _throw_failed_resp_span.set_attribute("status_message", "received_error_response")
                _throw_failed_resp_span.set_status(trace.StatusCode.ERROR, str(exc))
                attribute_span.record_exception(exc)
                raise exc

            if (
                response_status_code_str not in error_map
                and self._error_class_not_in_error_mapping(error_map, response_status_code)
            ):
                exc = APIError(
                    "The server returned an unexpected status code and no error class is registered"
                    f" for this code {response_status_code}",
                    response_status_code,
                    response_headers,  # type: ignore
                )
                attribute_span.record_exception(exc)
                raise exc
            _throw_failed_resp_span.set_attribute("status_message", "received_error_response")

            error = await self._get_error_from_response(
                response,
                error_map,
                response_status_code_str,
                response_status_code,
                attribute_span,
                _throw_failed_resp_span,
            )
            if isinstance(error, APIError):
                error.response_headers = response_headers  # type: ignore
                error.response_status_code = response_status_code
                exc = error
            else:
                exc = APIError(
                    (
                        "The server returned an unexpected status code and the error registered"
                        f" for this code failed to deserialize: {type(error)}"
                    ),
                    response_status_code,
                    response_headers,  # type: ignore
                )
            raise exc
        finally:
            _throw_failed_resp_span.end()

    async def get_http_response_message(
        self,
        request_info: RequestInformation,
        parent_span: trace.Span,
        claims: str = "",
    ) -> httpx.Response:
        _get_http_resp_span = self._start_local_tracing_span(
            "get_http_response_message", parent_span
        )

        self.set_base_url_for_request_information(request_info)

        additional_authentication_context = {}
        if claims:
            additional_authentication_context[self.CLAIMS_KEY] = claims

        await self._authentication_provider.authenticate_request(
            request_info, additional_authentication_context
        )

        request = self.get_request_from_request_information(
            request_info, _get_http_resp_span, parent_span
        )
        resp = await self._http_client.send(request)
        if not resp:
            raise ResponseError("Unable to get response from request")
        parent_span.set_attribute(HTTP_RESPONSE_STATUS_CODE, resp.status_code)
        if http_version := resp.http_version:
            parent_span.set_attribute(NETWORK_PROTOCOL_NAME, http_version)

        if content_length := resp.headers.get("Content-Length", None):
            parent_span.set_attribute("http.response.body.size", content_length)

        if content_type := resp.headers.get("Content-Type", None):
            parent_span.set_attribute("http.response.header.content-type", content_type)
        _get_http_resp_span.end()
        return await self.retry_cae_response_if_required(resp, request_info, claims)

    async def retry_cae_response_if_required(
        self, resp: httpx.Response, request_info: RequestInformation, claims: str
    ) -> httpx.Response:
        parent_span = self.start_tracing_span(request_info, "retry_cae_response_if_required")
        if (
            resp.status_code == 401
            and not claims  # previous claims exist. Means request has already been retried
            and resp.headers.get(self.RESPONSE_AUTH_HEADER)
        ):
            auth_header_value = resp.headers.get(self.RESPONSE_AUTH_HEADER)
            if auth_header_value.casefold().startswith(
                self.BEARER_AUTHENTICATION_SCHEME.casefold()
            ):
                claims_match = re.search('claims="([^"]+)"', auth_header_value)
                if not claims_match:
                    return resp
                response_claims = claims_match.group(1)
                parent_span.add_event(AUTHENTICATE_CHALLENGED_EVENT_KEY)
                parent_span.set_attribute("http.retry_count", 1)
                return await self.get_http_response_message(
                    request_info, parent_span, response_claims
                )
            return resp
        return resp

    def get_response_handler(self, request_info: RequestInformation) -> Any:
        response_handler_option = request_info.request_options.get(ResponseHandlerOption.get_key())
        if response_handler_option and isinstance(response_handler_option, ResponseHandlerOption):
            return response_handler_option.response_handler
        return None

    def set_base_url_for_request_information(self, request_info: RequestInformation) -> None:
        request_info.path_parameters["baseurl"] = self.base_url

    def get_request_from_request_information(
        self,
        request_info: RequestInformation,
        parent_span: trace.Span,
        attribute_span: trace.Span,
    ) -> httpx.Request:
        _get_request_span = self._start_local_tracing_span(
            "get_request_from_request_information", parent_span
        )
        url = parse.urlparse(request_info.url)
        method = request_info.http_method
        if not method:
            raise RequestError("HTTP method must be provided")

        otel_attributes = {
            HTTP_REQUEST_METHOD: method.value,
            SERVER_ADDRESS: url.hostname,
            URL_SCHEME: url.scheme,
            "url.uri_template": request_info.url_template,
        }

        if url.port is not None:
            otel_attributes["http.port"] = str(url.port)

        if self.observability_options.include_euii_attributes:
            otel_attributes.update({URL_FULL: url.geturl()})

        request = self._http_client.build_request(
            method=method.value,
            url=request_info.url,
            headers=request_info.request_headers,
            content=request_info.content,
        )
        request_options = {
            self.observability_options.get_key(): self.observability_options,
            "parent_span": parent_span,
            **request_info.request_options,
        }
        setattr(request, "options", request_options)

        if content_length := request.headers.get("Content-Length", None):
            otel_attributes.update({"http.request.body.size": content_length})

        if content_type := request.headers.get("Content-Type", None):
            otel_attributes.update({"http.request.header.content-type": content_type})
        attribute_span.set_attributes(otel_attributes)  # type: ignore
        _get_request_span.set_attributes(otel_attributes)  # type: ignore
        _get_request_span.end()

        return request

    async def convert_to_native_async(self, request_info: RequestInformation) -> httpx.Request:
        parent_span = self.start_tracing_span(request_info, "convert_to_native_async")
        try:
            if request_info is None:
                exc = ValueError("request information must be provided")
                parent_span.record_exception(exc)
                raise exc

            await self._authentication_provider.authenticate_request(request_info)

            request = self.get_request_from_request_information(
                request_info, parent_span, parent_span
            )
            return request
        finally:
            parent_span.end()

    def _error_class_not_in_error_mapping(
        self, error_map: dict[str, type[ParsableFactory]], status_code: int
    ) -> bool:
        """Helper function to check if the error class corresponding to a response status code
        is not in the error mapping.

        Args:
            error_map (dict[str, type[ParsableFactory]]): The error mapping.
            status_code (int): The response status code.

        Returns:
            bool: True if the error class is not in the error mapping, False otherwise.
        """

        return (
            (400 <= status_code < 500 and "4XX" not in error_map) or
            (500 <= status_code < 600 and "5XX" not in error_map)
        ) and ("XXX" not in error_map)
