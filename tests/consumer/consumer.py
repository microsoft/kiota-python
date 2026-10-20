from datetime import datetime
from typing import Callable, Optional, Union

import httpx
from azure.core.credentials import TokenCredential
from azure.core.credentials_async import AsyncTokenCredential
from kiota_abstractions.authentication import AnonymousAuthenticationProvider
from kiota_abstractions.request_information import RequestInformation
from kiota_abstractions.serialization import (
    Parsable,
    ParseNode,
    SerializationWriter,
    SerializationWriterFactory,
)
from kiota_abstractions.store import BackingStore, InMemoryBackingStoreFactory
from kiota_authentication_azure.azure_identity_authentication_provider import (
    AzureIdentityAuthenticationProvider,
)
from kiota_bundle.default_request_adapter import DefaultRequestAdapter
from kiota_http.httpx_request_adapter import HttpxRequestAdapter
from kiota_http.kiota_client_factory import KiotaClientFactory
from kiota_http.middleware import BaseMiddleware, RetryHandler
from kiota_http.middleware.options import RetryHandlerOption
from kiota_serialization_form.form_parse_node_factory import FormParseNodeFactory
from kiota_serialization_json.json_parse_node_factory import JsonParseNodeFactory
from kiota_serialization_json.json_serialization_writer_factory import JsonSerializationWriterFactory
from kiota_serialization_multipart.multipart_serialization_writer_factory import (
    MultipartSerializationWriterFactory,
)
from kiota_serialization_text.text_parse_node_factory import TextParseNodeFactory
from typing_extensions import assert_type


class User(Parsable):

    def __init__(self) -> None:
        self.display_name: Optional[str] = None

    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> "User":
        return User()

    def get_field_deserializers(self) -> dict[str, Callable[[ParseNode], None]]:
        return {"displayName": self.read_display_name}

    def read_display_name(self, parse_node: ParseNode) -> None:
        self.display_name = parse_node.get_str_value()

    def serialize(self, writer: SerializationWriter) -> None:
        writer.write_str_value("displayName", self.display_name)


async def check_request_adapter(request_info: RequestInformation) -> None:
    adapter = HttpxRequestAdapter(AnonymousAuthenticationProvider())
    assert_type(await adapter.convert_to_native_async(request_info), httpx.Request)
    assert_type(await adapter.send_async(request_info, User, None), Optional[User])
    assert_type(await adapter.send_collection_async(request_info, User, None), Optional[list[User]])
    assert_type(
        await adapter.send_collection_of_primitive_async(request_info, str, None), Optional[list[str]]
    )
    assert_type(await adapter.send_no_response_content_async(request_info, None), None)


def check_default_request_adapter() -> None:
    adapter = DefaultRequestAdapter(AnonymousAuthenticationProvider())
    assert_type(adapter.get_serialization_writer_factory(), SerializationWriterFactory)


async def check_azure_provider(
    credential: Union[TokenCredential, AsyncTokenCredential], request_info: RequestInformation
) -> None:
    provider = AzureIdentityAuthenticationProvider(credential, scopes=["https://graph.microsoft.com/.default"])
    assert_type(await provider.authenticate_request(request_info), None)


def check_middleware() -> None:
    assert_type(RetryHandlerOption().get_key(), str)
    assert_type(RetryHandler().options, RetryHandlerOption)
    assert_type(KiotaClientFactory.create_with_default_middleware(), httpx.AsyncClient)
    assert_type(KiotaClientFactory.get_default_middleware(None), list[BaseMiddleware])


def check_serialization() -> None:
    json_node = JsonParseNodeFactory().get_root_parse_node("application/json", b'{"displayName": "Ada"}')
    assert_type(json_node.get_object_value(User), User)
    assert_type(json_node.get_child_node("displayName"), Optional[ParseNode])
    text_node = TextParseNodeFactory().get_root_parse_node("text/plain", b"42")
    assert_type(text_node.get_str_value(), Optional[str])
    assert_type(text_node.get_int_value(), Optional[int])
    form_node = FormParseNodeFactory().get_root_parse_node("application/x-www-form-urlencoded", b"at=2026-10-20")
    assert_type(form_node.get_datetime_value(), Optional[datetime])
    json_writer = JsonSerializationWriterFactory().get_serialization_writer("application/json")
    assert_type(json_writer, SerializationWriter)
    multipart_writer = MultipartSerializationWriterFactory().get_serialization_writer("multipart/form-data")
    assert_type(multipart_writer, SerializationWriter)


def check_backing_store() -> None:
    assert_type(InMemoryBackingStoreFactory().create_backing_store(), BackingStore)
