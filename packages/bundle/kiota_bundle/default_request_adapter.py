from typing import Optional

import httpx
from kiota_abstractions.api_client_builder import (
    register_default_deserializer,
    register_default_serializer,
)
from kiota_abstractions.authentication import AuthenticationProvider
from kiota_abstractions.serialization import (
    ParseNodeFactory,
    ParseNodeFactoryRegistry,
    SerializationWriterFactory,
    SerializationWriterFactoryRegistry,
)
from kiota_http.httpx_request_adapter import HttpxRequestAdapter
from kiota_http.kiota_client_factory import KiotaClientFactory
from kiota_serialization_form.form_parse_node_factory import FormParseNodeFactory
from kiota_serialization_form.form_serialization_writer_factory import (
    FormSerializationWriterFactory,
)
from kiota_serialization_json.json_parse_node_factory import JsonParseNodeFactory
from kiota_serialization_json.json_serialization_writer_factory import (
    JsonSerializationWriterFactory,
)
from kiota_serialization_multipart.multipart_serialization_writer_factory import (
    MultipartSerializationWriterFactory,
)
from kiota_serialization_text.text_parse_node_factory import TextParseNodeFactory
from kiota_serialization_text.text_serialization_writer_factory import (
    TextSerializationWriterFactory,
)
"""
The default client request adapter.
"""


class DefaultRequestAdapter(HttpxRequestAdapter):

    def __init__(
        self,
        authentication_provider: AuthenticationProvider,
        parse_node_factory: Optional[ParseNodeFactory] = None,
        serialization_writer_factory: Optional[SerializationWriterFactory] = None,
        http_client: Optional[httpx.AsyncClient] = None
    ) -> None:
        if parse_node_factory is None:
            parse_node_factory = ParseNodeFactoryRegistry()
        if serialization_writer_factory is None:
            serialization_writer_factory = SerializationWriterFactoryRegistry()
        if http_client is None:
            http_client = KiotaClientFactory.create_with_default_middleware()

        super().__init__(
            authentication_provider=authentication_provider,
            parse_node_factory=parse_node_factory,
            serialization_writer_factory=serialization_writer_factory,
            http_client=http_client
        )
        self.__setup_defaults()

    def __setup_defaults(self) -> None:
        register_default_serializer(JsonSerializationWriterFactory)
        register_default_serializer(TextSerializationWriterFactory)
        register_default_serializer(FormSerializationWriterFactory)
        register_default_serializer(MultipartSerializationWriterFactory)
        register_default_deserializer(JsonParseNodeFactory)
        register_default_deserializer(TextParseNodeFactory)
        register_default_deserializer(FormParseNodeFactory)
