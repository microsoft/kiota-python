import json
from unittest.mock import Mock

import pytest
from kiota_abstractions.request_information import RequestInformation

from kiota_serialization_json.json_serialization_writer import JsonSerializationWriter
from kiota_serialization_json.json_serialization_writer_factory import (
    JsonSerializationWriterFactory,
)


@pytest.mark.parametrize("value", [None, False, 0, 0.0, "", [], {}, True, 1, "text", [1]])
def test_root_value_round_trip_and_reset(value):
    writer = JsonSerializationWriter()
    writer.write_any_value(None, value)
    result = json.loads(writer.get_serialized_content())
    assert type(result) is type(value)
    assert result == value
    # A named property after serialization verifies that root state was reset.
    writer.write_str_value("name", "next")
    assert json.loads(writer.get_serialized_content()) == {"name": "next"}


@pytest.mark.parametrize("value", [None, False, 0, 0.0, "", [], {}, True, 1, "text", [1]])
def test_rejects_mixed_root_and_property_values(value):
    writer = JsonSerializationWriter()
    writer.write_any_value(None, value)
    writer.write_str_value("name", "property")
    with pytest.raises(ValueError, match="Invalid Json output"):
        writer.get_serialized_content()


@pytest.mark.parametrize("value", [False, 0, 0.0, "", []])
def test_request_content_preserves_falsy_scalar_values(value):
    adapter = Mock()
    adapter.get_serialization_writer_factory.return_value = JsonSerializationWriterFactory()
    request = RequestInformation()
    request.set_content_from_scalar(adapter, "application/json", value)
    result = json.loads(request.content)
    assert type(result) is type(value)
    assert result == value


def test_composed_object_can_serialize_root_null():
    model = Mock()
    model.serialize.side_effect = lambda output: output.write_null_value(None)
    writer = JsonSerializationWriter()
    writer.write_object_value("wrapped", model)
    assert json.loads(writer.get_serialized_content()) == {"wrapped": None}
