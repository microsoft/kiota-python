# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All Rights Reserved.
# Licensed under the MIT License.
# See License in the project root for license information.
# ------------------------------------------------------------------------------

from unittest.mock import Mock

import pytest

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
    factories = {registered_type: factory}
    if registered_type.casefold() != "application/json":
        factories["application/json"] = fallback
    monkeypatch.setattr(registry, "CONTENT_TYPE_ASSOCIATED_FACTORIES", factories)

    assert registry.get_serialization_writer(content_type) is factory.get_serialization_writer.return_value
    factory.get_serialization_writer.assert_called_once_with(registered_type)
    fallback.get_serialization_writer.assert_not_called()
