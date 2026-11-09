# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All Rights Reserved.
# Licensed under the MIT License.
# See License in the project root for license information.
# ------------------------------------------------------------------------------

from unittest.mock import Mock

import pytest

from kiota_abstractions.api_client_builder import register_default_deserializer

from kiota_abstractions.serialization import ParseNode, ParseNodeFactory, ParseNodeFactoryRegistry


def test_registry_dispatches_empty_content(monkeypatch):
    registry = ParseNodeFactoryRegistry()
    mock_node = Mock(spec=ParseNode)
    mock_factory = Mock(spec=ParseNodeFactory)
    mock_factory.get_valid_content_type.return_value = "text/plain"
    mock_factory.get_root_parse_node.return_value = mock_node

    monkeypatch.setitem(registry.CONTENT_TYPE_ASSOCIATED_FACTORIES, "text/plain", mock_factory)

    result = registry.get_root_parse_node("text/plain", b"")
    assert result is mock_node
    mock_factory.get_root_parse_node.assert_called_once_with("text/plain", b"")


def test_registry_raises_on_none_content():
    registry = ParseNodeFactoryRegistry()
    with pytest.raises(Exception) as exc_info:
        registry.get_root_parse_node("text/plain", None)
    assert "Content cannot be null" in str(exc_info.value)


def test_registry_raises_on_empty_content_type():
    registry = ParseNodeFactoryRegistry()
    with pytest.raises(Exception) as exc_info:
        registry.get_root_parse_node("", b"hello")
    assert "Content type cannot be null" in str(exc_info.value)


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
    registry = ParseNodeFactoryRegistry()
    factory = Mock(spec=ParseNodeFactory)
    fallback = Mock(spec=ParseNodeFactory)
    factory.get_valid_content_type.return_value = registered_type
    fallback.get_valid_content_type.return_value = "application/json"
    monkeypatch.setattr(registry, "CONTENT_TYPE_ASSOCIATED_FACTORIES", {})
    register_default_deserializer(lambda: factory)
    if registered_type.lower() != "application/json":
        register_default_deserializer(lambda: fallback)
    assert registered_type.lower() in registry.CONTENT_TYPE_ASSOCIATED_FACTORIES

    assert registry.get_root_parse_node(content_type, b"{}") is factory.get_root_parse_node.return_value
    factory.get_root_parse_node.assert_called_once_with(registered_type, b"{}")
    fallback.get_root_parse_node.assert_not_called()


def test_registration_keeps_lookup_constant_time(monkeypatch):
    class NoScanDict(dict):
        def items(self):
            raise AssertionError("Lookup must not scan registrations")

    registry = ParseNodeFactoryRegistry()
    factory = Mock(spec=ParseNodeFactory)
    factory.get_valid_content_type.return_value = "Application/Custom+Json"
    monkeypatch.setattr(registry, "CONTENT_TYPE_ASSOCIATED_FACTORIES", NoScanDict())
    register_default_deserializer(lambda: factory)

    assert "application/custom+json" in registry.CONTENT_TYPE_ASSOCIATED_FACTORIES
    assert registry.get_root_parse_node("APPLICATION/CUSTOM+JSON", b"{}") is factory.get_root_parse_node.return_value
    factory.get_root_parse_node.assert_called_once_with("Application/Custom+Json", b"{}")


def test_direct_exact_key_registration_still_works(monkeypatch):
    registry = ParseNodeFactoryRegistry()
    factory = Mock(spec=ParseNodeFactory)
    factory.get_valid_content_type.return_value = "Application/Custom"
    monkeypatch.setattr(registry, "CONTENT_TYPE_ASSOCIATED_FACTORIES", {"Application/Custom": factory})

    assert registry.get_root_parse_node("Application/Custom", b"{}") is factory.get_root_parse_node.return_value
    factory.get_root_parse_node.assert_called_once_with("Application/Custom", b"{}")


def test_direct_alias_keeps_its_registered_media_type(monkeypatch):
    registry = ParseNodeFactoryRegistry()
    factory = Mock(spec=ParseNodeFactory)
    factory.get_valid_content_type.return_value = "application/json"
    monkeypatch.setattr(registry, "CONTENT_TYPE_ASSOCIATED_FACTORIES", {"application/vnd.custom+json": factory})

    assert registry.get_root_parse_node("application/vnd.custom+json", b"{}") is factory.get_root_parse_node.return_value
    factory.get_root_parse_node.assert_called_once_with("application/vnd.custom+json", b"{}")


def test_registry_factory_does_not_need_one_declared_type(monkeypatch):
    registry = ParseNodeFactoryRegistry()
    nested = Mock(spec=ParseNodeFactoryRegistry)
    nested.get_valid_content_type.side_effect = Exception("Registry has no single media type")
    monkeypatch.setattr(registry, "CONTENT_TYPE_ASSOCIATED_FACTORIES", {"application/json": nested})

    assert registry.get_root_parse_node("application/json", b"{}") is nested.get_root_parse_node.return_value
    nested.get_valid_content_type.assert_not_called()
    nested.get_root_parse_node.assert_called_once_with("application/json", b"{}")
