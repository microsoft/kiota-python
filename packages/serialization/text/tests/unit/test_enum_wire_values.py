from enum import Enum

import pytest

from kiota_serialization_text.text_parse_node_factory import TextParseNodeFactory
from kiota_serialization_text.text_serialization_writer import TextSerializationWriter


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
    writer = TextSerializationWriter()
    writer.write_enum_value(None, member)
    node = TextParseNodeFactory().get_root_parse_node("text/plain", writer.get_serialized_content())
    assert node.get_enum_value(WireStatus) is member


def test_enum_value_lookup_preserves_name_fallback_and_unknown_error():
    factory = TextParseNodeFactory()
    known = factory.get_root_parse_node("text/plain", b"Known")
    assert known.get_enum_value(DefaultingStatus) is DefaultingStatus.Known
    with pytest.raises(Exception, match="Invalid key"):
        factory.get_root_parse_node("text/plain", b"not-a-member").get_enum_value(DefaultingStatus)


def test_enum_without_options_retains_empty_and_unknown_behavior():
    factory = TextParseNodeFactory()
    assert factory.get_root_parse_node("text/plain", b"").get_enum_value(EmptyStatus) is None
    with pytest.raises(Exception, match="Invalid key"):
        factory.get_root_parse_node("text/plain", b"unknown").get_enum_value(EmptyStatus)
