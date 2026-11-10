# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All Rights Reserved.
# Licensed under the MIT License.
# See License in the project root for license information.
# ------------------------------------------------------------------------------

from unittest.mock import Mock

import pytest

from kiota_abstractions.api_client_builder import register_default_serializer

from kiota_abstractions.serialization import (
    SerializationWriterFactory,
    SerializationWriterFactoryRegistry,
)


@pytest.mark.parametrize("content_type,registered_type", [
    ("application/json", "application/json"),
    ("APPLICATION/JSON", "application/json"),
    ("Application/Json;charset=UTF-8", "application/json"),
    ("APPLICATION/VND.MICROSOFT+JSON", "application/json"),
    ("application/vnd.microsoft+json;version=1", "application/json"),
    ("APPLICATION/VND.MICROSOFT+JSON", "application/vnd.microsoft+json"),
    ("Application/Vnd.Microsoft+Json", "Application/Vnd.Microsoft+Json"),
    ("APPLICATION/VND.MICROSOFT+JSON", "Application/Vnd.Microsoft+Json"),
    ("APPLICATION/JSON", "Application/Json"),
])
def test_registry_matches_media_type_case_insensitively(monkeypatch, content_type, registered_type):
    registry = SerializationWriterFactoryRegistry()
    factory = Mock(spec=SerializationWriterFactory)
    fallback = Mock(spec=SerializationWriterFactory)
    factory.get_valid_content_type.return_value = registered_type
    fallback.get_valid_content_type.return_value = "application/json"
    monkeypatch.setattr(registry, "CONTENT_TYPE_ASSOCIATED_FACTORIES", {})
    register_default_serializer(lambda: factory)
    if registered_type.lower() != "application/json":
        register_default_serializer(lambda: fallback)
    assert registered_type.lower() in registry.CONTENT_TYPE_ASSOCIATED_FACTORIES

    assert registry.get_serialization_writer(content_type) is factory.get_serialization_writer.return_value
    factory.get_serialization_writer.assert_called_once_with(registered_type)
    fallback.get_serialization_writer.assert_not_called()


def test_registration_keeps_lookup_constant_time(monkeypatch):
    class NoScanDict(dict):
        def items(self):
            raise AssertionError("Lookup must not scan registrations")

    registry = SerializationWriterFactoryRegistry()
    factory = Mock(spec=SerializationWriterFactory)
    factory.get_valid_content_type.return_value = "Application/Custom+Json"
    monkeypatch.setattr(registry, "CONTENT_TYPE_ASSOCIATED_FACTORIES", NoScanDict())
    register_default_serializer(lambda: factory)

    assert "application/custom+json" in registry.CONTENT_TYPE_ASSOCIATED_FACTORIES
    assert registry.get_serialization_writer("APPLICATION/CUSTOM+JSON") is factory.get_serialization_writer.return_value
    factory.get_serialization_writer.assert_called_once_with("Application/Custom+Json")


def test_direct_exact_key_registration_still_works(monkeypatch):
    registry = SerializationWriterFactoryRegistry()
    factory = Mock(spec=SerializationWriterFactory)
    factory.get_valid_content_type.return_value = "Application/Custom"
    monkeypatch.setattr(registry, "CONTENT_TYPE_ASSOCIATED_FACTORIES", {"Application/Custom": factory})

    assert registry.get_serialization_writer("Application/Custom") is factory.get_serialization_writer.return_value
    factory.get_serialization_writer.assert_called_once_with("Application/Custom")


def test_direct_alias_keeps_its_registered_media_type(monkeypatch):
    registry = SerializationWriterFactoryRegistry()
    factory = Mock(spec=SerializationWriterFactory)
    factory.get_valid_content_type.return_value = "application/json"
    monkeypatch.setattr(registry, "CONTENT_TYPE_ASSOCIATED_FACTORIES", {"application/vnd.custom+json": factory})

    assert registry.get_serialization_writer("application/vnd.custom+json") is factory.get_serialization_writer.return_value
    factory.get_serialization_writer.assert_called_once_with("application/vnd.custom+json")


def test_registry_factory_does_not_need_one_declared_type(monkeypatch):
    registry = SerializationWriterFactoryRegistry()
    nested = Mock(spec=SerializationWriterFactoryRegistry)
    nested.get_valid_content_type.side_effect = Exception("Registry has no single media type")
    monkeypatch.setattr(registry, "CONTENT_TYPE_ASSOCIATED_FACTORIES", {"application/json": nested})

    assert registry.get_serialization_writer("application/json") is nested.get_serialization_writer.return_value
    nested.get_valid_content_type.assert_not_called()
    nested.get_serialization_writer.assert_called_once_with("application/json")
