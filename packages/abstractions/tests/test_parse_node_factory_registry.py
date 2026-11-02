# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All Rights Reserved.
# Licensed under the MIT License.
# See License in the project root for license information.
# ------------------------------------------------------------------------------

from unittest.mock import Mock

import pytest

from kiota_abstractions.serialization import ParseNode, ParseNodeFactory, ParseNodeFactoryRegistry


def test_registry_dispatches_empty_content():
    registry = ParseNodeFactoryRegistry()
    mock_node = Mock(spec=ParseNode)
    mock_factory = Mock(spec=ParseNodeFactory)
    mock_factory.get_root_parse_node.return_value = mock_node

    registry.CONTENT_TYPE_ASSOCIATED_FACTORIES["text/plain"] = mock_factory

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
