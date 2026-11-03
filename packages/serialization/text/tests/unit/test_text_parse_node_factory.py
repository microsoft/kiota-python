import pytest

from kiota_serialization_text.text_parse_node import TextParseNode
from kiota_serialization_text.text_parse_node_factory import TextParseNodeFactory
from kiota_serialization_text.text_serialization_writer import TextSerializationWriter


@pytest.fixture
def sample_text_string():
    return 'Microsoft Graph'


def test_get_root_parse_node(sample_text_string):
    factory = TextParseNodeFactory()
    sample_text_string_bytes = sample_text_string.encode('utf-8')
    root = factory.get_root_parse_node('text/plain', sample_text_string_bytes)
    assert isinstance(root, TextParseNode)


def test_get_root_parse_node_no_content_type(sample_text_string):
    with pytest.raises(Exception) as e_info:
        factory = TextParseNodeFactory()
        sample_text_string_bytes = sample_text_string.encode('utf-8')
        root = factory.get_root_parse_node('', sample_text_string_bytes)


def test_get_root_parse_node_unsupported_content_type(sample_text_string):
    with pytest.raises(Exception) as e_info:
        factory = TextParseNodeFactory()
        sample_text_string_bytes = sample_text_string.encode('utf-8')
        root = factory.get_root_parse_node('application/xml', sample_text_string_bytes)


def test_get_root_parse_node_empty_text():
    factory = TextParseNodeFactory()
    sample_string_bytes = ''.encode('utf-8')
    root = factory.get_root_parse_node('text/plain', sample_string_bytes)
    assert isinstance(root, TextParseNode)
    assert root.get_str_value() == ''
    assert root.get_bytes_value() == b''


def test_get_root_parse_node_none_content():
    with pytest.raises(TypeError):
        factory = TextParseNodeFactory()
        factory.get_root_parse_node('text/plain', None)


def test_get_valid_content_type():
    factory = TextParseNodeFactory()
    content_type = factory.get_valid_content_type()
    assert content_type == 'text/plain'


def test_empty_string_round_trip():
    writer = TextSerializationWriter()
    writer.write_str_value(None, '')
    content = writer.get_serialized_content()
    factory = TextParseNodeFactory()
    node = factory.get_root_parse_node('text/plain', content)
    assert node.get_str_value() == ''


def test_empty_bytes_round_trip():
    writer = TextSerializationWriter()
    writer.write_bytes_value(None, b'')
    content = writer.get_serialized_content()
    factory = TextParseNodeFactory()
    node = factory.get_root_parse_node('text/plain', content)
    assert node.get_bytes_value() == b''
