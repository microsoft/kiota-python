from enum import Enum

import pytest

from kiota_serialization_json.json_parse_node_factory import JsonParseNodeFactory
from kiota_serialization_json.json_serialization_writer import JsonSerializationWriter


class WireStatus(Enum):
    NotStarted = "not-started"
    Ready = "running"
    Running = "ready"
    Empty = ""


class DefaultingStatus(Enum):
    Known = "wire-known"
    Unknown = "unknown"

    @classmethod
    def _missing_(cls, value):
        return cls.Unknown


class EmptyStatus(str, Enum):
    pass


@pytest.mark.parametrize("member", list(WireStatus))
def test_enum_writer_reader_round_trip(member):
    writer = JsonSerializationWriter()
    writer.write_enum_value("status", member)
    root = JsonParseNodeFactory().get_root_parse_node(
        "application/json", writer.get_serialized_content()
    )
    assert root.get_child_node("status").get_enum_value(WireStatus) is member


def test_enum_array_uses_declared_wire_values():
    values = [WireStatus.NotStarted, WireStatus.Ready, WireStatus.Empty]
    writer = JsonSerializationWriter()
    writer.write_collection_of_enum_values("statuses", values)
    root = JsonParseNodeFactory().get_root_parse_node(
        "application/json", writer.get_serialized_content()
    )
    assert root.get_child_node("statuses").get_collection_of_enum_values(WireStatus) == values


def test_enum_csv_uses_declared_wire_values():
    node = JsonParseNodeFactory().get_root_parse_node("application/json", b'"not-started,running"')
    assert node.get_collection_of_enum_values(WireStatus) == [
        WireStatus.NotStarted, WireStatus.Ready
    ]


def test_enum_value_lookup_preserves_name_fallback_and_unknown_result():
    factory = JsonParseNodeFactory()
    known = factory.get_root_parse_node("application/json", b'"Known"')
    unknown = factory.get_root_parse_node("application/json", b'"not-a-member"')
    assert known.get_enum_value(DefaultingStatus) is DefaultingStatus.Known
    assert unknown.get_enum_value(DefaultingStatus) is None


@pytest.mark.parametrize("payload", [b'null', b'""', b'"unknown"'])
def test_enum_without_options_retains_no_value(payload):
    node = JsonParseNodeFactory().get_root_parse_node("application/json", payload)
    assert node.get_enum_value(EmptyStatus) is None
