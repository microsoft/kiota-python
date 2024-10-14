import pytest

from kiota_serialization_multipart.multipart_serialization_writer import MultipartSerializationWriter
from kiota_serialization_multipart.multipart_serialization_writer_factory import (
    MultipartSerializationWriterFactory,
)

MULTIPART_CONTENT_TYPE = 'multipart/form-data'
def test_get_serialization_writer():
    factory = MultipartSerializationWriterFactory()
    writer = factory.get_serialization_writer(MULTIPART_CONTENT_TYPE)
    assert isinstance(writer, MultipartSerializationWriter)


def test_get_serialization_writer_no_content_type():
    with pytest.raises(TypeError) as e_info:
        factory = MultipartSerializationWriterFactory()
        factory.get_serialization_writer('')
    assert str(e_info.value) == 'Content Type cannot be null'


def test_get_serialization_writer_unsupported_content_type():
    with pytest.raises(Exception) as e_info:
        factory = MultipartSerializationWriterFactory()
        factory.get_serialization_writer('application/xml')
    assert str(e_info.value) == f'Expected {MULTIPART_CONTENT_TYPE} as content type'


def test_get_valid_content_type():
    factory = MultipartSerializationWriterFactory()
    content_type = factory.get_valid_content_type()
    assert content_type == MULTIPART_CONTENT_TYPE