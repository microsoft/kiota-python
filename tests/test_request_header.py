import pytest

from kiota_abstractions.request_headers import RequestHeaders

def test_defensive():
    """Tests initialization of RequestHeader objects
    """
    headers = RequestHeaders()
    with pytest.raises(ValueError):
        headers.try_get(None)
    with pytest.raises(ValueError):
        headers.try_get("")
    with pytest.raises(ValueError):
        headers.get(None)
    with pytest.raises(ValueError):
        headers.get("")
    with pytest.raises(ValueError):
        headers.try_add(None, "value")
    with pytest.raises(ValueError):
        headers.try_add("", "value")
    with pytest.raises(ValueError):
        headers.try_add("header", None)
    with pytest.raises(ValueError):
        headers.add_all(None)
    with pytest.raises(ValueError):
        headers.add(None, "value")
    with pytest.raises(ValueError):
        headers.add("", "value")
    with pytest.raises(ValueError):
        headers.add("header", None)
    with pytest.raises(ValueError):
        headers.remove_value(None, "value")
    with pytest.raises(ValueError):
        headers.remove_value("", "value")
    with pytest.raises(ValueError):
        headers.remove_value("header", None)
    with pytest.raises(ValueError):
        headers.remove(None)
    with pytest.raises(ValueError):
        headers.remove("")
    with pytest.raises(ValueError):
        headers.contains(None)
    with pytest.raises(ValueError):
        headers.contains("")
        
def test_normalizes_casing():
    headers = RequestHeaders()
    headers.add("heaDER1", "value1")
    assert {"value1"} <= headers.try_get("header1")
    assert {"value1"} <= headers.get("header1")
    
def test_adds_to_non_existent_header():
    """Tests adding a header to a non-existent header
    """
    headers = RequestHeaders()
    headers.add("header1", "value1")
    assert {"value1"} <= headers.try_get("header1")
    assert {"value1"} <= headers.get("header1")
    assert headers.contains("header1")
    assert headers.count() == 1
    
def test_try_adds_to_non_existent_header():
    """Tests try adding a header to a non-existent header
    """
    headers = RequestHeaders()
    assert headers.try_add("header1", "value1")
    assert {"value1"} <= headers.try_get("header1")
    assert {"value1"} <= headers.get("header1")
    assert headers.contains("header1")
    assert headers.count() == 1
    
def test_adds_to_existing_header():
    """Tests adding a header to an existing header
    """
    headers = RequestHeaders()
    headers.add("header1", "value1")
    headers.add("header1", "value2")
    assert {"value1", "value2"} <= headers.try_get("header1")
    assert {"value1", "value2"} <= headers.get("header1")
    assert headers.contains("header1")
    assert headers.count() == 1
        
def test_try_adds_to_existing_header():
    """Tests try adding a header to an existing header
    """
    headers = RequestHeaders()
    assert headers.try_add("header1", "value1")
    assert not headers.try_add("header1", "value2")
    assert {"value1"} <= headers.try_get("header1")
    assert {"value1"} <= headers.get("header1")
    assert headers.contains("header1")
    assert headers.count() == 1
    
def test_add_single_value_header_to_existing_header():
    """Tests adding a single value header to an existing header
    """
    headers = RequestHeaders()
    headers.add("content-type", "value1")
    headers.add("content-type", "value2")
    assert {"value2"} <= headers.try_get("content-type")
    assert {"value2"} <= headers.get("content-type")
    assert headers.contains("content-type")
    assert headers.count() == 1
    
def test_try_add_single_value_header_to_existing_header():
    """Tests adding a single value header to an existing header
    """
    headers = RequestHeaders()
    headers.try_add("content-type", "value1")
    headers.try_add("content-type", "value2")
    assert {"value1"} <= headers.try_get("content-type")
    assert {"value1"} <= headers.get("content-type")
    assert headers.contains("content-type")
    assert headers.count() == 1
    
def test_removes_value_from_existing_header():
    """Tests removing a value from an existing header
    """
    headers = RequestHeaders()
    headers.remove_value("header1", "value1")
    headers.add("header1", "value1")
    headers.add("header1", "value2")
    assert headers.contains("header1")
    assert headers.count() == 1
    headers.remove_value("header1", "value1")
    assert {"value2"} <= headers.try_get("header1")
    headers.remove_value("header1", "value2")
    assert not headers.contains("header1")
    assert headers.count() == 0
    
def test_removes_header():
    """Tests removing a header
    """
    headers = RequestHeaders()
    headers.add("header1", "value1")
    headers.add("header1", "value2")
    assert headers.contains("header1")
    assert headers.count() == 1
    headers.remove("header1")
    assert not headers.contains("header1")
    assert headers.count() == 0
    
def test_clears_headers():
    """Tests clearing headers
    """
    headers = RequestHeaders()
    headers.add("header1", "value1")
    headers.add("header1", "value2")
    headers.add("header2", "value3")
    headers.add("header2", "value4")
    assert headers.contains("header1")
    assert headers.contains("header2")
    assert headers.count() == 2
    headers.clear()
    assert not headers.contains("header1")
    assert not headers.contains("header2")
    assert headers.count() == 0
    assert headers.keys() == []
    
def test_adds_headers_from_instance():
    """Tests adding headers from another instance
    """
    headers = RequestHeaders()
    headers.add("header1", "value1")
    headers.add("header1", "value2")
    headers.add("header2", "value3")
    headers.add("header2", "value4")
    assert headers.contains("header1")
    assert headers.contains("header2")
    assert headers.count() == 2
    headers2 = RequestHeaders()
    headers2.add("header3", "value5")
    headers2.add("header3", "value6")
    headers2.add("header4", "value7")
    headers2.add("header4", "value8")
    headers.add_all(headers2)
    assert headers.contains("header1")
    assert headers.contains("header2")
    assert headers.contains("header3")
    assert headers.contains("header4")
    assert headers.count() == 4
    assert headers.keys() == ["header1", "header2", "header3", "header4"]