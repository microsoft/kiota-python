import pytest

from kiota_abstractions.headers_collection import HeadersCollection


def test_defensive():
    """Tests initialization of RequestHeader objects
    """
    headers = HeadersCollection()
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
    headers = HeadersCollection()
    headers.add("heaDER1", "value1")
    assert {"value1"} <= headers.try_get("header1")
    assert {"value1"} <= headers.get("header1")
    
def test_adds_to_non_existent_header():
    """Tests adding a header to a non-existent header
    """
    headers = HeadersCollection()
    headers.add("header1", "value1")
    assert {"value1"} <= headers.try_get("header1")
    assert {"value1"} <= headers.get("header1")
    assert headers.contains("header1")
    assert headers.count() == 1
    
def test_try_adds_to_non_existent_header():
    """Tests try adding a header to a non-existent header
    """
    headers = HeadersCollection()
    assert headers.try_add("header1", "value1")
    assert {"value1"} <= headers.try_get("header1")
    assert {"value1"} <= headers.get("header1")
    assert headers.contains("header1")
    assert headers.count() == 1
    
def test_adds_to_existing_header():
    """Tests adding a header to an existing header
    """
    headers = HeadersCollection()
    headers.add("header1", "value1")
    headers.add("header1", "value2")
    assert {"value1", "value2"} <= headers.try_get("header1")
    assert {"value1", "value2"} <= headers.get("header1")
    assert headers.contains("header1")
    assert headers.count() == 1
        
def test_try_adds_to_existing_header():
    """Tests try adding a header to an existing header
    """
    headers = HeadersCollection()
    assert headers.try_add("header1", "value1")
    assert not headers.try_add("header1", "value2")
    assert {"value1"} <= headers.try_get("header1")
    assert {"value1"} <= headers.get("header1")
    assert headers.contains("header1")
    assert headers.count() == 1
    
def test_add_single_value_header_to_existing_header():
    """Tests adding a single value header to an existing header
    """
    headers = HeadersCollection()
    headers.add("content-type", "value1")
    headers.add("content-type", "value2")
    assert headers.try_get("content-type") == {"value2"}
    assert headers.get("content-type") == {"value2"}
    assert headers.contains("content-type")
    assert headers.count() == 1
    
def test_try_add_single_value_header_to_existing_header():
    """Tests adding a single value header to an existing header
    """
    headers = HeadersCollection()
    headers.try_add("content-type", "value1")
    headers.try_add("content-type", "value2")
    assert {"value1"} <= headers.try_get("content-type")
    assert {"value1"} <= headers.get("content-type")
    assert headers.contains("content-type")
    assert headers.count() == 1
    
def test_removes_value_from_existing_header():
    """Tests removing a value from an existing header
    """
    headers = HeadersCollection()
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
    headers = HeadersCollection()
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
    headers = HeadersCollection()
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
    headers = HeadersCollection()
    headers.add("header1", "value1")
    headers.add("header1", "value2")
    headers.add("header2", "value3")
    headers.add("header2", "value4")
    assert headers.contains("header1")
    assert headers.contains("header2")
    assert headers.count() == 2
    headers2 = HeadersCollection()
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


def test_add_all_replaces_single_value_header():
    """Tests that add_all keeps a single value header to one value
    """
    headers = HeadersCollection()
    headers.add("Content-Type", "application/json")
    other = HeadersCollection()
    other.add("Content-Type", "text/plain")
    headers.add_all(other)
    assert headers.get("content-type") == {"text/plain"}


def test_init_with_dict():
    """Tests initialization of HeadersCollection with a dict"""
    headers = HeadersCollection({"header1": "value1", "header2": ["value2", "value3"]})
    assert headers.count() == 2
    assert "header1" in headers
    assert "header2" in headers
    assert headers["header1"] == {"value1"}
    assert headers["header2"] == {"value2", "value3"}


def test_init_with_headers_collection():
    """Tests initialization of HeadersCollection with another HeadersCollection"""
    source = HeadersCollection({"header1": "value1"})
    copy_headers = HeadersCollection(source)
    assert copy_headers.count() == 1
    assert "header1" in copy_headers
    assert copy_headers["header1"] == {"value1"}


def test_init_with_empty_inputs():
    """Tests that initializing with empty mapping or empty HeadersCollection does not fail"""
    headers_dict = HeadersCollection({})
    assert headers_dict.count() == 0
    assert len(headers_dict) == 0

    empty_source = HeadersCollection()
    headers_copy = HeadersCollection(empty_source)
    assert headers_copy.count() == 0
    assert len(headers_copy) == 0


def test_init_iterable_single_value_header():
    """Tests that initializing with an iterable for single-value headers retains only the first value"""
    headers = HeadersCollection({"Content-Length": ["10", "20"]})
    assert headers.get("content-length") == {"10"}
    assert headers["content-length"] == {"10"}


def test_add_all_with_dict():
    """Tests adding headers from a dictionary"""
    headers = HeadersCollection()
    headers.add_all({"header1": "value1", "header2": ["value2", "value3"]})
    assert headers.count() == 2
    assert headers.get("header1") == {"value1"}
    assert headers.get("header2") == {"value2", "value3"}


def test_add_all_empty_inputs():
    """Tests that add_all with empty collection or empty mapping is a no-op and does not raise"""
    headers = HeadersCollection({"header1": "value1"})
    headers.add_all({})
    assert headers.count() == 1
    headers.add_all(HeadersCollection())
    assert headers.count() == 1


def test_container_methods():
    """Tests container magic methods (__contains__, __getitem__, __setitem__, __len__, __iter__)"""
    headers = HeadersCollection()
    headers["header1"] = "value1"
    headers["header2"] = ["val2", "val3"]
    assert len(headers) == 2
    assert "header1" in headers
    assert "header2" in headers
    assert "nonexistent" not in headers
    assert headers["header1"] == {"value1"}
    assert headers["header2"] == {"val2", "val3"}
    assert list(headers) == ["header1", "header2"]
    with pytest.raises(KeyError):
        _ = headers["nonexistent"]


def test_subscript_assignment_replaces_values():
    """Tests that subscript assignment replaces existing values rather than appending, across casing"""
    headers = HeadersCollection()
    headers["Authorization"] = "old"
    assert headers["authorization"] == {"old"}
    headers["authorization"] = "new"
    assert headers["authorization"] == {"new"}
    assert headers.get("authorization") == {"new"}
    assert len(headers) == 1

    headers["AUTHORIZATION"] = ["token1", "token2"]
    assert headers["authorization"] == {"token1", "token2"}
    assert len(headers) == 1


def test_subscript_assignment_validation():
    """Tests that invalid key or value raises ValueError before modifying stored headers"""
    headers = HeadersCollection()
    headers["Authorization"] = "valid"

    with pytest.raises(ValueError):
        headers[None] = "value"
    with pytest.raises(ValueError):
        headers[""] = "value"
    with pytest.raises(ValueError):
        headers["Authorization"] = None

    # Stored value remains intact
    assert headers["authorization"] == {"valid"}


def test_subscript_assignment_single_value_header():
    """Tests that subscript assignment respects SINGLE_VALUE_HEADERS"""
    headers = HeadersCollection()
    headers["Content-Type"] = ["application/json", "text/plain"]
    assert headers["content-type"] == {"application/json"}

