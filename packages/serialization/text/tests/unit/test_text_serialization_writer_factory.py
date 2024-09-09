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
