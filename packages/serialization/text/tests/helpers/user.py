from __future__ import annotations

from datetime import date, datetime
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, TypeVar

from kiota_abstractions.serialization import (
    AdditionalDataHolder,
    Parsable,
    ParseNode,
    SerializationWriter,
)

from .office_location import OfficeLocation

T = TypeVar('T')


@dataclass
class User(Parsable, AdditionalDataHolder):

    id: Optional[str] = None
    display_name: Optional[str] = None
    office_location: Optional[OfficeLocation] = None
    updated_at: Optional[datetime] = None
    birthday: Optional[date] = None
    business_phones: Optional[list[str]] = None
    mobile_phone: Optional[str] = None
    is_active: Optional[bool] = None
    age: Optional[int] = None
    gpa: Optional[float] = None
    additional_data: dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def create_from_discriminator_value(parse_node: Optional[ParseNode] = None) -> User:
        """
        Creates a new instance of the appropriate class based on discriminator value
        Args:
            parseNode: The parse node to use to read the discriminator value and create the object
        Returns: Attachment
        """
        if not parse_node:
            raise Exception("parse_node cannot be undefined")
        return User()

    def get_field_deserializers(self) -> dict[str, Callable[[ParseNode], None]]:
        """Gets the deserialization information for this object.

        Returns:
            dict[str, Callable[[ParseNode], None]]: The deserialization information for this
            object where each entry is a property key with its deserialization callback.
        """
        return {
            "id":
            lambda n: setattr(self, 'id', n.get_uuid_value()),
            "display_name":
            lambda n: setattr(self, 'display_name', n.get_str_value()),
            "office_location":
            lambda n: setattr(self, 'office_location', n.get_enum_value(OfficeLocation)),
            "updated_at":
            lambda n: setattr(self, 'updated_at', n.get_datetime_value()),
            "birthday":
            lambda n: setattr(self, 'birthday', n.get_date_value()),
            "business_phones":
            lambda n: setattr(self, 'business_phones', n.get_collection_of_primitive_values(str)),
            "mobile_phone":
            lambda n: setattr(self, 'mobile_phone', n.get_str_value()),
            "is_active":
            lambda n: setattr(self, 'is_active', n.get_bool_value()),
            "age":
            lambda n: setattr(self, 'age', n.get_int_value()),
            "gpa":
            lambda n: setattr(self, 'gpa', n.get_float_value())
        }

    def serialize(self, writer: SerializationWriter) -> None:
        """Writes the objects properties to the current writer.

        Args:
            writer (SerializationWriter): The writer to write to.
        """
        if not writer:
            raise Exception("Writer cannot be undefined")
        writer.write_uuid_value("id", self.id)
        writer.write_str_value("display_name", self.display_name)
        writer.write_enum_value("office_location", self.office_location)
        writer.write_datetime_value("updated_at", self.updated_at)
        writer.write_date_value("birthday", self.birthday)
        writer.write_collection_of_primitive_values("business_phones", self.business_phones)
        writer.write_str_value("mobile_phone", self.mobile_phone)
        writer.write_bool_value("is_active", self.is_active)
        writer.write_int_value("age", self.age)
        writer.write_float_value("gpa", self.gpa)
