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
def test_get_serialization_writer_with_parameters_and_case_variants(content_type):
    factory = FormSerializationWriterFactory()
    writer = factory.get_serialization_writer(content_type)
    assert isinstance(writer, FormSerializationWriter)


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
        factory = FormSerializationWriterFactory()
        factory.get_serialization_writer(content_type)
    assert str(e_info.value) == f"Expected {FORM_CONTENT_TYPE} as content type"
