import pytest

from kiota_serialization_form.form_parse_node import FormParseNode
from kiota_serialization_form.form_parse_node_factory import FormParseNodeFactory


FORM_CONTENT_TYPE = "application/x-www-form-urlencoded"

@pytest.fixture
def sample_form_string():
    return "name=Tesla&age=2&city=New+York"


def test_get_root_parse_node(sample_form_string):
    factory = FormParseNodeFactory()
    sample_form_string_bytes = sample_form_string.encode('utf-8')
    root = factory.get_root_parse_node(FORM_CONTENT_TYPE, sample_form_string_bytes)
    assert isinstance(root, FormParseNode)

  
def test_get_root_parse_node_no_content_type(sample_form_string):
    with pytest.raises(Exception) as e_info:
        factory = FormParseNodeFactory()
        sample_form_string_bytes = sample_form_string.encode('utf-8')
        root = factory.get_root_parse_node('', sample_form_string_bytes)
    assert str(e_info.value) == "Content Type cannot be null"


def test_get_root_parse_node_unsupported_content_type(sample_form_string):
    with pytest.raises(Exception) as e_info:
        factory = FormParseNodeFactory()
        sample_form_string_bytes = sample_form_string.encode('utf-8')
        root = factory.get_root_parse_node('application/xml', sample_form_string_bytes)
    assert str(e_info.value) == f"Expected {FORM_CONTENT_TYPE} as content type"


def test_get_root_parse_node_empty_form():
    with pytest.raises(TypeError) as e_info:
        factory = FormParseNodeFactory()
        sample_string_bytes = ''.encode('utf-8')
        root = factory.get_root_parse_node(FORM_CONTENT_TYPE, sample_string_bytes)
    assert str(e_info.value) == "Content cannot be null"


def test_get_valid_content_type():
    factory = FormParseNodeFactory()
    content_type = factory.get_valid_content_type()
    assert content_type == FORM_CONTENT_TYPE


@pytest.mark.parametrize(
    "content_type",
    [
        "application/x-www-form-urlencoded; charset=utf-8",
        "application/x-www-form-urlencoded; charset=UTF-8",
        "application/x-www-form-urlencoded ; charset=utf-8",
        "APPLICATION/X-WWW-FORM-URLENCODED",
        "APPLICATION/X-WWW-FORM-URLENCODED; CHARSET=UTF-8",
        "Application/x-www-form-urlencoded; charset=utf-8",
    ],
)
def test_get_root_parse_node_with_parameters_and_case_variants(sample_form_string, content_type):
    factory = FormParseNodeFactory()
    sample_form_string_bytes = sample_form_string.encode('utf-8')
    root = factory.get_root_parse_node(content_type, sample_form_string_bytes)
    assert isinstance(root, FormParseNode)


@pytest.mark.parametrize(
    "content_type",
    [
        ";",
        ";;",
        "; charset=utf-8",
        "   ; charset=utf-8",
    ],
)
def test_get_root_parse_node_delimiter_only(sample_form_string, content_type):
    with pytest.raises(TypeError) as e_info:
        factory = FormParseNodeFactory()
        sample_form_string_bytes = sample_form_string.encode('utf-8')
        factory.get_root_parse_node(content_type, sample_form_string_bytes)
    assert str(e_info.value) == f"Expected {FORM_CONTENT_TYPE} as content type"
