from __future__ import annotations

from datetime import date, datetime
from typing import Any, Callable, Dict, List, Optional, TypeVar

from kiota_abstractions.serialization import (
    AdditionalDataHolder,
    Parsable,
    ParsableFactory,
    ParseNode,
    SerializationWriter,
)

from .office_location import OfficeLocation

T = TypeVar('T')


class MockResponseObject(Parsable, AdditionalDataHolder):

    def __init__(self) -> None:
        self._id: Optional[str] = None
        self._display_name: Optional[str] = None
        self._office_location: Optional[OfficeLocation] = None
        self._updated_at: Optional[datetime] = None
        self._birthday: Optional[date] = None
        self._business_phones: Optional[List[str]] = None
        self._mobile_phone: Optional[str] = None
        self._is_active: Optional[bool] = None
        self._age: Optional[int] = None
        self._gpa: Optional[float] = None
        self._additional_data: Dict[str, Any] = {}

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, new_id):
        self._id = new_id

    @property
    def display_name(self):
        return self._display_name

    @display_name.setter
    def display_name(self, new_display_name):
        self._display_name = new_display_name

    @property
    def office_location(self):
        return self._office_location

    @office_location.setter
    def office_location(self, new_office_location):
        self._office_location = new_office_location

    @property
    def updated_at(self):
        return self._updated_at

    @updated_at.setter
    def updated_at(self, new_updated_at):
        self._updated_at = new_updated_at

    @property
    def birthday(self):
        return self._birthday

    @birthday.setter
    def birthday(self, new_birthday):
        self._birthday = new_birthday

    @property
    def business_phones(self):
        return self._business_phones

    @business_phones.setter
    def business_phones(self, new_business_phones):
        self._business_phones = new_business_phones

    @property
    def mobile_phone(self):
        return self._mobile_phone

    @mobile_phone.setter
    def mobile_phone(self, new_mobile_phone):
        self._mobile_phone = new_mobile_phone

    @property
    def is_active(self):
        return self._is_active

    @is_active.setter
    def is_active(self, new_is_active):
        self._is_active = new_is_active

    @property
    def age(self):
        return self._age

    @age.setter
    def age(self, new_age):
        self._age = new_age

    @property
    def gpa(self):
        return self._gpa

    @gpa.setter
    def gpa(self, new_gpa):
        self._gpa = new_gpa

    @property
    def additional_data(self) -> Dict[str, Any]:
        return self._additional_data

    @additional_data.setter
    def additional_data(self, data: Dict[str, Any]) -> None:
        self._additional_data = data

    def get_object_value(self, model_class):
        return self

    def get_collection_of_object_values(self, model_class):
        return [self, self]

    def get_collection_of_primitive_values(self, primitive_type):
        return [12.1, 12.2, 12.3, 12.4, 12.5]

    def get_float_value(self):
        return 22.3

    @staticmethod
    def create_from_discriminator_value(
        parse_node: Optional[ParseNode] = None
    ) -> MockResponseObject:
        """
        Creates a new instance of the appropriate class based on discriminator value
        Args:
            parseNode: The parse node to use to read the discriminator value and create the object
        Returns: Attachment
        """
        if not parse_node:
            raise Exception("parse_node cannot be undefined")
        return MockResponseObject()

    def get_field_deserializers(self) -> Optional[Dict[str, Callable[[ParseNode], None]]]:
        """Gets the deserialization information for this object.

        Returns:
            Dict[str, Callable[[ParseNode], None]]: The deserialization information for this
            object where each entry is a property key with its deserialization callback.
        """
        pass

    def serialize(self, writer: SerializationWriter) -> None:
        """Writes the objects properties to the current writer.

        Args:
            writer (SerializationWriter): The writer to write to.
        """
        pass


class MockErrorObject():

    @staticmethod
    def get_object_value(model_class):
        return model_class
