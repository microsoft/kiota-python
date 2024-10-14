import json
from uuid import UUID

import pytest

from kiota_serialization_json.json_parse_node import JsonParseNode
from kiota_serialization_json.json_serialization_writer import JsonSerializationWriter

from ..helpers import OfficeLocation, User, User2
from ..helpers.intersection_type import InterSectionType

display_name = "John Doe"


def test_parse_intersection_type_complex_property1():
    json_string = '{"id": "8f841f30-e6e3-439a-a812-ebd369559c36",\
        "display_name": "John Doe", "age": 32, "gpa": 3.9, "office_location": "dunhill"}'

    parse_node = JsonParseNode(json.loads(json_string))
    result = parse_node.get_object_value(InterSectionType)

    assert result.composed_type1
    assert result.composed_type2
    assert not result.composed_type3
    assert not result.string_value
    assert result.composed_type1.id == UUID("8f841f30-e6e3-439a-a812-ebd369559c36")
    assert result.composed_type1.office_location == OfficeLocation.Dunhill
    assert result.composed_type2.display_name == display_name
    assert result.composed_type2.age == 32


def test_parse_intersection_type_complex_property2():
    json_string = '{"id": 43, "display_name": "John Doe", "age": 32, "gpa": 3.9,\
        "office_location": "oval"}'

    parse_node = JsonParseNode(json.loads(json_string))
    result = parse_node.get_object_value(InterSectionType)

    assert result.composed_type1
    assert result.composed_type2
    assert not result.composed_type3
    assert not result.string_value
    assert not result.composed_type1.id
    assert result.composed_type1.office_location == OfficeLocation.Oval
    assert not result.composed_type2.id
    assert result.composed_type2.display_name == display_name
    assert result.composed_type2.age == 32


def test_parse_intersection_type_complex_property3():
    json_string = '[{"id": "8f841f30-e6e3-439a-a812-ebd369559c36",\
        "display_name": "John Doe", "age": 32, "gpa": 3.9, "office_location": "dunhill"},\
            {"id": "8f841f30-e6e3-439a-a812-ebd369559c36", "display_name": "Jane Doe",\
                "age": 30, "gpa": 3.8, "office_location": "oval"}]'

    parse_node = JsonParseNode(json.loads(json_string))
    result = parse_node.get_object_value(InterSectionType)

    assert not result.composed_type1
    assert not result.composed_type2
    assert result.composed_type3
    assert not result.string_value
    assert len(result.composed_type3) == 2
    assert result.composed_type3[1].office_location == OfficeLocation.Oval
    assert result.composed_type3[0].office_location == OfficeLocation.Dunhill


def test_parse_intersection_type_string_value():
    json_string = json.dumps(display_name)
    parse_node = JsonParseNode(json.loads(json_string))
    result = parse_node.get_object_value(InterSectionType)

    assert not result.composed_type1
    assert not result.composed_type2
    assert not result.composed_type3
    assert result.string_value
    assert result.string_value == display_name


def test_serializes_intersection_type_string_value():
    writer = JsonSerializationWriter()
    model = InterSectionType(string_value=display_name)
    model.serialize(writer)

    content = writer.get_serialized_content()
    content_string = content.decode('utf-8')
    assert content_string == json.dumps(display_name)


def test_serializes_intersection_type():
    writer = JsonSerializationWriter()
    composed_type1 = User(
        id=UUID("8f841f30-e6e3-439a-a812-ebd369559c36"), office_location=OfficeLocation.Dunhill
    )
    composed_type2 = User2(display_name=display_name, age=32)
    model = InterSectionType(composed_type1=composed_type1, composed_type2=composed_type2)
    model.serialize(writer)

    content = writer.get_serialized_content()
    content_string = content.decode('utf-8')
    assert content_string == '{"id": "8f841f30-e6e3-439a-a812-ebd369559c36", '\
        '"office_location": "dunhill", "display_name": "John Doe", "age": 32}'


def test_serializes_intersection_type_complex_property2():
    writer = JsonSerializationWriter()
    composed_type2 = User2(id=1, display_name=display_name, age=32)
    model = InterSectionType(composed_type2=composed_type2)
    model.serialize(writer)

    content = writer.get_serialized_content()
    content_string = content.decode('utf-8')
    assert content_string == '{"id": 1, "display_name": "John Doe", "age": 32}'


def test_serializes_intersection_type_complex_property3():
    writer = JsonSerializationWriter()
    user_1 = User(
        id=UUID("8f841f30-e6e3-439a-a812-ebd369559c36"),
        office_location=OfficeLocation.Dunhill,
        is_active=True
    )
    user_2 = User(
        id=UUID("7031ea06-d26d-4c9a-a738-ce6fe524f05f"),
        office_location=OfficeLocation.Oval,
        is_active=False
    )
    model = InterSectionType(composed_type3=[user_1, user_2])
    model.serialize(writer)

    content = writer.get_serialized_content()
    content_string = content.decode('utf-8')
    assert content_string == '[{"id": "8f841f30-e6e3-439a-a812-ebd369559c36", '\
        '"office_location": "dunhill", "is_active": true}, '\
            '{"id": "7031ea06-d26d-4c9a-a738-ce6fe524f05f", "office_location": "oval", '\
                '"is_active": false}]'
