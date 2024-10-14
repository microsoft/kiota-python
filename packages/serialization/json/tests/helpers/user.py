from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Callable, Dict, List, Optional, TypeVar
from uuid import UUID

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
    additional_data: Dict[str, Any] = field(default_factory=dict)
    id: Optional[UUID] = None
    office_location: Optional[OfficeLocation] = None
    updated_at: Optional[datetime] = None
    birthday: Optional[date] = None
    business_phones: Optional[List[str]] = None
    mobile_phone: Optional[str] = None
    is_active: Optional[bool] = None

    @staticmethod
    def create_from_discriminator_value(parse_node: Optional[ParseNode] = None) -> User:
        """
        Creates a new instance of the appropriate class based on discriminator value
        Args:
            parseNode: The parse node to use to read the discriminator value and create the object
        Returns: Attachment
        """
        if not parse_node:
            raise TypeError("parse_node cannot be null")
        return User()

    def get_field_deserializers(self) -> Dict[str, Callable[[ParseNode], None]]:
        """Gets the deserialization information for this object.

        Returns:
            Dict[str, Callable[[ParseNode], None]]: The deserialization information for this
            object where each entry is a property key with its deserialization callback.
        """
        return {
            "id":
            lambda n: setattr(self, 'id', n.get_uuid_value()),
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
        }

    def serialize(self, writer: SerializationWriter) -> None:
        """Writes the objects properties to the current writer.

        Args:
            writer (SerializationWriter): The writer to write to.
        """
        if not writer:
            raise TypeError("Writer cannot be null")
        writer.write_uuid_value("id", self.id)
        writer.write_enum_value("office_location", self.office_location)
        writer.write_datetime_value("updated_at", self.updated_at)
        writer.write_date_value("birthday", self.birthday)
        writer.write_collection_of_primitive_values("business_phones", self.business_phones)
        writer.write_str_value("mobile_phone", self.mobile_phone)
        writer.write_bool_value("is_active", self.is_active)
