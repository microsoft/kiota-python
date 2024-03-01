import pytest

from kiota_abstractions.serialization import SerializationWriter
from kiota_abstractions.multipart_body import MultipartBody
def test_defensive():
    """Tests initialization of MultipartBody objects
    """
    multipart = MultipartBody()
    with pytest.raises(ValueError) as excinfo:
        multipart.add_or_replace_part(None, "text/plain", "Hello, World!")
    assert "Part name cannot be null" in str(excinfo.value)
    with pytest.raises(ValueError) as excinfo:
        multipart.add_or_replace_part("text", None, "Hello, World!")
    assert "Content type cannot be null" in str(excinfo.value)
    with pytest.raises(ValueError) as excinfo:
        multipart.add_or_replace_part("text", "text/plain", None)
    assert "Part value cannot be null" in str(excinfo.value)
    with pytest.raises(ValueError) as excinfo:
        multipart.get_part_value(None)
    assert "Part name cannot be null" in str(excinfo.value)
    with pytest.raises(ValueError) as excinfo:
        multipart.get_part_value("")
    assert "Part name cannot be null" in str(excinfo.value)
    with pytest.raises(ValueError) as excinfo:
        multipart.remove_part(None)
    assert "Part name cannot be null" in str(excinfo.value)
    with pytest.raises(ValueError) as excinfo:
        multipart.remove_part("")
    assert "Part name cannot be null" in str(excinfo.value)
    with pytest.raises(ValueError) as excinfo:
        multipart.serialize(None)
    assert "Serialization writer cannot be null" in str(excinfo.value)
    
def test_add_or_replace_part():
    """Tests adding or replacing a part in the multipart body
    """
    multipart = MultipartBody()
    multipart.add_or_replace_part("text", "text/plain", "Hello, World!")
    assert multipart.get_part_value("text") == "Hello, World!"
    multipart.add_or_replace_part("text", "text/plain", "Hello, World! 2")
    assert multipart.get_part_value("text") == "Hello, World! 2"

def test_remove_part():
    """Tests removing a part from the multipart body
    """
    multipart = MultipartBody()
    multipart.add_or_replace_part("text", "text/plain", "Hello, World!")
    assert multipart.get_part_value("text") == "Hello, World!"
    assert multipart.remove_part("text")
    assert not multipart.get_part_value("text")
    assert not multipart.remove_part("text")