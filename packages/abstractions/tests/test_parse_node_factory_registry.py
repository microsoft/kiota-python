# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All Rights Reserved.
# Licensed under the MIT License.
# See License in the project root for license information.
# ------------------------------------------------------------------------------

from unittest.mock import Mock

import pytest

from kiota_abstractions.serialization import ParseNode, ParseNodeFactory, ParseNodeFactoryRegistry


def test_registry_dispatches_empty_content(monkeypatch):
    registry = ParseNodeFactoryRegistry()
    mock_node = Mock(spec=ParseNode)
    mock_factory = Mock(spec=ParseNodeFactory)
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
    factories = {registered_type: factory}
    if registered_type.casefold() != "application/json":
        factories["application/json"] = fallback
    monkeypatch.setattr(registry, "CONTENT_TYPE_ASSOCIATED_FACTORIES", factories)

    assert registry.get_root_parse_node(content_type, b"{}") is factory.get_root_parse_node.return_value
    factory.get_root_parse_node.assert_called_once_with(registered_type, b"{}")
    fallback.get_root_parse_node.assert_not_called()
