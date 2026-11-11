import json

import pytest

from kiota_serialization_json.json_parse_node import JsonParseNode
from kiota_serialization_json.json_parse_node_factory import JsonParseNodeFactory


@pytest.fixture
def sample_json_string():
    return '{"name":"Tesla", "age":2, "city":"New York"}'


def test_get_root_parse_node(sample_json_string):
    factory = JsonParseNodeFactory()
    sample_json_string_bytes = sample_json_string.encode('utf-8')
    root = factory.get_root_parse_node('application/json', sample_json_string_bytes)
    assert isinstance(root, JsonParseNode)
    assert root._json_node == json.loads(sample_json_string)


def test_get_root_parse_node_no_content_type(sample_json_string):
    with pytest.raises(Exception):
        factory = JsonParseNodeFactory()
        sample_json_string_bytes = sample_json_string.encode('utf-8')
        factory.get_root_parse_node('', sample_json_string_bytes)


def test_get_root_parse_node_unsupported_content_type(sample_json_string):
    with pytest.raises(Exception):
        factory = JsonParseNodeFactory()
        sample_json_string_bytes = sample_json_string.encode('utf-8')
        factory.get_root_parse_node('application/xml', sample_json_string_bytes)


def test_get_root_parse_node_empty_json():
    with pytest.raises(TypeError):
        factory = JsonParseNodeFactory()
        sample_string_bytes = ''.encode('utf-8')
        factory.get_root_parse_node('application/json', sample_string_bytes)


def test_get_valid_content_type():
    factory = JsonParseNodeFactory()
    content_type = factory.get_valid_content_type()
    assert content_type == 'application/json'


@pytest.mark.parametrize(
    "content_type",
    [
        "application/json; charset=utf-8",
        "application/json; charset=UTF-8",
        "application/json;odata.metadata=minimal",
        "application/json; odata=verbose",
        "application/json ; charset=utf-8",
        "APPLICATION/JSON",
        "APPLICATION/JSON; CHARSET=UTF-8",
        "Application/json; charset=utf-8",
    ],
)
def test_get_root_parse_node_with_parameters_and_case_variants(sample_json_string, content_type):
    factory = JsonParseNodeFactory()
    sample_json_string_bytes = sample_json_string.encode('utf-8')
    root = factory.get_root_parse_node(content_type, sample_json_string_bytes)
    assert isinstance(root, JsonParseNode)
    assert root._json_node == json.loads(sample_json_string)


@pytest.mark.parametrize(
    "content_type",
    [
        ";",
        ";;",
        "; charset=utf-8",
        "   ; charset=utf-8",
    ],
)
def test_get_root_parse_node_delimiter_only(sample_json_string, content_type):
    with pytest.raises(TypeError) as e_info:
        factory = JsonParseNodeFactory()
        sample_json_string_bytes = sample_json_string.encode('utf-8')
        factory.get_root_parse_node(content_type, sample_json_string_bytes)
    assert str(e_info.value) == "Expected application/json as content type"

