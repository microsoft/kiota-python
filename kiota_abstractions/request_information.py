from dataclasses import dataclass, fields
from datetime import date, datetime, time, timedelta
from io import BytesIO
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Set, TypeVar, Union
from urllib.parse import unquote
from uuid import UUID

from opentelemetry import trace
from stduritemplate import StdUriTemplate

from ._version import VERSION
from .method import Method
from .request_option import RequestOption
from .serialization import Parsable, SerializationWriter

if TYPE_CHECKING:
    from .request_adapter import RequestAdapter

Url = str
T = TypeVar("T", bound=Parsable)
OBSERVABILITY_TRACER_NAME = "microsoft-python-kiota-abstractions"
tracer = trace.get_tracer(OBSERVABILITY_TRACER_NAME, VERSION)


@dataclass
class QueryParams:
    pass


class RequestInformation:
    """This class represents an abstract HTTP request"""

    RAW_URL_KEY = "request-raw-url"
    BINARY_CONTENT_TYPE = "application/octet-stream"
    CONTENT_TYPE_HEADER = "Content-Type"
    REQUEST_TYPE_KEY = "com.microsoft.kiota.request.type"

    def __init__(self) -> None:
        # The uri of the request
        self.__uri: Optional[Url] = None

        self.__request_options: Dict[str, RequestOption] = {}

        # The path parameters for the current request
        self.path_parameters: Dict[str, Any] = {}

        # The URL template for the request
        self.url_template: Optional[str] = None

        # The HTTP Method for the request
        self.http_method: Optional[Method] = None

        # The query parameters for the request
        self.query_parameters: Dict[str, QueryParams] = {}

        # The Request Headers
        self.headers: Dict[str, Set[str]] = {}  # Use set to remove duplicates

        # The Request Body
        self.content: Optional[BytesIO] = None

    @property
    def url(self) -> Url:
        """Gets the URL of the request"""
        raw_url = self.path_parameters.get(self.RAW_URL_KEY)
        if self.__uri:
            return self.__uri
        if raw_url:
            return raw_url
        if self.query_parameters is None:
            raise Exception("Query parameters cannot be null")
        if self.path_parameters is None:
            raise Exception("Path parameters cannot be null")
        if not self.url_template:
            raise Exception("Url Template cannot be null")

        data: Dict[str, Any] = {}
        for key, val in self.query_parameters.items():
            data[key] = val
        for key, val in self.path_parameters.items():
            data[key] = val

        result = StdUriTemplate.expand(self.url_template, data)
        return result

    @url.setter
    def url(self, url: Url) -> None:
        """Sets the URL of the request"""
        if not url:
            raise Exception("Url cannot be undefined")
        self.__uri = url
        self.query_parameters.clear()
        self.path_parameters.clear()

    @property
    def request_headers(self) -> Optional[Dict]:
        final = {}
        for key, value in self.headers.items():
            final[key] = ", ".join(value)
        return final

    def add_request_headers(
        self, headers_to_add: Optional[Dict[str, Union[str, List[str]]]]
    ) -> None:
        """Adds headers to the request"""
        if headers_to_add:
            for key, value in headers_to_add.items():
                lowercase_key = key.lower()
                if lowercase_key in self.headers:
                    if isinstance(value, list):
                        self.headers[lowercase_key] = self.headers[lowercase_key].union(set(value))
                    else:
                        self.headers[lowercase_key].add(str(value))
                else:
                    if isinstance(value, list):
                        self.headers[lowercase_key] = set(value)
                    else:
                        self.headers[lowercase_key] = {str(value)}

    def remove_request_headers(self, key: str) -> None:
        """Removes a request header from the current request

        Args:
            key (str): The key of the header to remove
        """
        if key and key.lower() in self.headers:
            del self.headers[key.lower()]

    @property
    def request_options(self) -> Dict[str, RequestOption]:
        """Gets the request options for the request."""
        return self.__request_options

    def add_request_options(self, options: List[RequestOption]) -> None:
        if not options:
            return
        for option in options:
            self.__request_options[option.get_key()] = option

    def remove_request_options(self, options: List[RequestOption]) -> None:
        if not options:
            return
        for option in options:
            del self.__request_options[option.get_key()]

    def set_content_from_parsable(
        self,
        request_adapter: Optional["RequestAdapter"],
        content_type: Optional[str],
        values: Union[T, List[T]],
    ) -> None:
        """Sets the request body from a model with the specified content type.

        Args:
            request_adapter (Optional[RequestAdapter]): The adapter service to get the serialization
            writer from.
            content_type (Optional[str]): the content type.
            values (Union[T, List[T]]): the models.
        """
        with tracer.start_as_current_span(
            self._create_parent_span_name("set_content_from_parsable")
        ) as span:
            writer = self._get_serialization_writer(request_adapter, content_type, values, span)

            if isinstance(values, list):
                writer.write_collection_of_object_values(None, values)
                span.set_attribute(self.REQUEST_TYPE_KEY, "[]")
            else:
                writer.write_object_value(None, values)
                span.set_attribute(self.REQUEST_TYPE_KEY, "{}")

            self._set_content_and_content_type_header(writer, content_type)

    def set_content_from_scalar(
        self,
        request_adapter: Optional["RequestAdapter"],
        content_type: Optional[str],
        values: Union[T, List[T]],
    ) -> None:
        """Sets the request body from a scalar value with the specified content type.

        Args:
            request_adapter (Optional[RequestAdapter]): The adapter service to get the serialization
            writer from.
            content_type (Optional[str]): the content type to set.
            values (Union[T, List[T]]): the scalar values to serialize
        """
        with tracer.start_as_current_span(
            self._create_parent_span_name("set_content_from_scalar")
        ) as span:
            writer = self._get_serialization_writer(request_adapter, content_type, values, span)

            if isinstance(values, list):
                writer.writer = writer.write_collection_of_primitive_values(None, values)
                span.set_attribute(self.REQUEST_TYPE_KEY, "[]")
            else:
                function_values: Dict[type, Callable] = {
                    bool: writer.write_bool_value,
                    str: writer.write_str_value,
                    int: writer.write_int_value,
                    float: writer.write_float_value,
                    UUID: writer.write_uuid_value,
                    datetime: writer.write_datetime_value,
                    date: writer.write_date_value,
                    timedelta: writer.write_timedelta_value,
                    time: writer.write_time_value,
                }
                value_type = type(values)
                span.set_attribute(self.REQUEST_TYPE_KEY, value_type.__name__)
                writer_func = function_values.get(value_type, None)
                if writer_func is None:
                    exc = ValueError(
                        f"Encountered an unknown type during serialization {value_type}"
                    )
                    span.record_exception(exc)
                    raise exc
                writer_func(None, values)
            self._set_content_and_content_type_header(writer, content_type)

    def set_stream_content(self, value: BytesIO) -> None:
        """Sets the request body to be a binary stream.

        Args:
            value (BytesIO): the binary stream
        """
        self.headers[self.CONTENT_TYPE_HEADER] = {self.BINARY_CONTENT_TYPE}
        self.content = value

    def set_query_string_parameters_from_raw_object(self, q: Optional[QueryParams]) -> None:
        if q:
            for field in fields(q):
                key = field.name
                if hasattr(q, "get_query_parameter"):
                    serialization_key = q.get_query_parameter(key)  # type: ignore
                    if serialization_key:
                        key = serialization_key
                self.query_parameters[key] = getattr(q, field.name)

    def _get_serialization_writer(
        self,
        request_adapter: Optional["RequestAdapter"],
        content_type: Optional[str],
        values: Union[T, List[T]],
        parent_span: trace.Span,
    ):
        """_summary_

        Args:
            request_adapter (RequestAdapter): _description_
            content_type (str): _description_
            values (Union[T, List[T]]): _description_
        """
        _span = self._start_local_tracing_span("_get_serialization_writer", parent_span)
        try:
            if not request_adapter:
                exc = ValueError("RequestAdapter cannot be null")
                _span.record_exception(exc)
                raise exc
            if not content_type:
                exc = ValueError("Content Type cannot be null")
                _span.record_exception(exc)
                raise exc
            if not values:
                exc = ValueError("Values cannot be null")
                _span.record_exception(exc)
                raise exc
            return request_adapter.get_serialization_writer_factory(
            ).get_serialization_writer(content_type)
        finally:
            _span.end()

    def _set_content_and_content_type_header(
        self, writer: SerializationWriter, content_type: Optional[str]
    ):
        if content_type:
            self.headers[self.CONTENT_TYPE_HEADER] = {content_type}
        self.content = writer.get_serialized_content()

    def _decode_uri_string(self, uri: Optional[str]) -> str:
        """Decodes a URI encoded string."""
        if uri and "%" in uri:
            return unquote(uri)
        return ""

    def _create_parent_span_name(self, method: str) -> str:
        """Creates a parent span name for the given method."""
        uri_template = self._decode_uri_string(self.url_template)
        parent_span_name = f"{method} - {uri_template}"
        return parent_span_name

    def _start_local_tracing_span(self, name: str, parent_span: trace.Span) -> trace.Span:
        """Helper method to start a span locally with the parent context."""
        _context = trace.set_span_in_context(parent_span)
        span = tracer.start_span(name, context=_context)
        return span
