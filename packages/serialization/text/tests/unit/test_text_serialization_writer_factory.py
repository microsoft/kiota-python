import pytest
from kiota_abstractions.serialization import SerializationWriterFactory

from kiota_serialization_text.text_serialization_writer import TextSerializationWriter
from kiota_serialization_text.text_serialization_writer_factory import (
    TextSerializationWriterFactory,
)


def test_get_serialization_writer():
    factory = TextSerializationWriterFactory()
    writer = factory.get_serialization_writer('text/plain')
    assert isinstance(writer, TextSerializationWriter)


def test_get_serialization_writer_no_content_type():
    with pytest.raises(TypeError) as e_info:
        factory = TextSerializationWriterFactory()
        writer = factory.get_serialization_writer("")


def test_get_serialization_writer_unsupported_content_type():
    with pytest.raises(Exception) as e_info:
        factory = TextSerializationWriterFactory()
        writer = factory.get_serialization_writer('application/xml')


def test_get_valid_content_type():
    factory = TextSerializationWriterFactory()
    content_type = factory.get_valid_content_type()
    assert content_type == 'text/plain'


@pytest.mark.parametrize(
    "content_type",
    [
        "text/plain; charset=utf-8",
        "text/plain; charset=UTF-8",
        "text/plain ; charset=utf-8",
        "TEXT/PLAIN",
        "TEXT/PLAIN; CHARSET=UTF-8",
        "Text/plain; charset=utf-8",
    ],
)
def test_get_serialization_writer_with_parameters_and_case_variants(content_type):
    factory = TextSerializationWriterFactory()
    writer = factory.get_serialization_writer(content_type)
    assert isinstance(writer, TextSerializationWriter)


@pytest.mark.parametrize(
    "content_type",
    [
        ";",
        ";;",
        "; charset=utf-8",
        "   ; charset=utf-8",
    ],
)
def test_get_serialization_writer_delimiter_only(content_type):
    with pytest.raises(TypeError) as e_info:
        factory = TextSerializationWriterFactory()
        factory.get_serialization_writer(content_type)
    assert str(e_info.value) == "Expected text/plain as content type"

