import pytest

from kiota_serialization_form.form_serialization_writer import FormSerializationWriter
from kiota_serialization_form.form_serialization_writer_factory import (
    FormSerializationWriterFactory,
)

FORM_CONTENT_TYPE = 'application/x-www-form-urlencoded'
def test_get_serialization_writer():
    factory = FormSerializationWriterFactory()
    writer = factory.get_serialization_writer(FORM_CONTENT_TYPE)
    assert isinstance(writer, FormSerializationWriter)


def test_get_serialization_writer_no_content_type():
    with pytest.raises(TypeError) as e_info:
        factory = FormSerializationWriterFactory()
        factory.get_serialization_writer('')
    assert str(e_info.value) == 'Content Type cannot be null'


def test_get_serialization_writer_unsupported_content_type():
    with pytest.raises(Exception) as e_info:
        factory = FormSerializationWriterFactory()
        factory.get_serialization_writer('application/xml')
    assert str(e_info.value) == f'Expected {FORM_CONTENT_TYPE} as content type'


def test_get_valid_content_type():
    factory = FormSerializationWriterFactory()
    content_type = factory.get_valid_content_type()
    assert content_type == FORM_CONTENT_TYPE