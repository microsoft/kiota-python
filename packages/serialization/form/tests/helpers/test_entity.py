from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, time
from collections.abc import Callable
from typing import Any, Optional, TypeVar
from uuid import UUID

from kiota_abstractions.serialization import (
    AdditionalDataHolder,
    Parsable,
    ParseNode,
    SerializationWriter,
)

from .test_enum import TestEnum

T = TypeVar('T')

@dataclass
class TestEntity(Parsable, AdditionalDataHolder):
    additional_data: dict[str, Any] = field(default_factory=dict)
    id: Optional[UUID] = None
    device_names: Optional[list[str]] = None
    numbers: Optional[TestEnum] = None
    work_duration: Optional[timedelta] = None
    birthday: Optional[date] = None
    start_work_time: Optional[time] = None
    end_work_time: Optional[time] = None
    created_date_time: Optional[datetime] = None
    office_location: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: Optional[ParseNode] = None) -> TestEntity:
        """
        Creates a new instance of the appropriate class based on discriminator value
        Args:
            parseNode: The parse node to use to read the discriminator value and create the object
        Returns: Attachment
        """
        if not parse_node:
            raise TypeError("parse_node cannot be null")
        return TestEntity()

    def get_field_deserializers(self) -> dict[str, Callable[[ParseNode], None]]:
        """Gets the deserialization information for this object.

        Returns:
            dict[str, Callable[[ParseNode], None]]: The deserialization information for this
            object where each entry is a property key with its deserialization callback.
        """
        return {
            "id": lambda x: setattr(self, "id", x.get_uuid_value()),
            "deviceNames": lambda x: setattr(self, "device_names", x.get_collection_of_primitive_values(str)),
            "numbers": lambda x: setattr(self, "numbers", x.get_enum_value(TestEnum)),
            "workDuration": lambda x: setattr(self, "work_duration", x.get_timedelta_value()),
            "birthDay": lambda x: setattr(self, "birthday", x.get_date_value()),
            "startWorkTime": lambda x: setattr(self, "start_work_time", x.get_time_value()),
            "endWorkTime": lambda x: setattr(self, "end_work_time", x.get_time_value()),
            "createdDateTime": lambda x: setattr(self, "created_date_time", x.get_datetime_value()),
            "officeLocation": lambda x: setattr(self, "office_location", x.get_str_value()),
        }

    def serialize(self, writer: SerializationWriter) -> None:
        """Writes the objects properties to the current writer.

        Args:
            writer (SerializationWriter): The writer to write to.
        """
        if not writer:
            raise TypeError("Writer cannot be null")
        writer.write_uuid_value("id", self.id)
        writer.write_collection_of_primitive_values("deviceNames", self.device_names)
        writer.write_enum_value("numbers", self.numbers)
        writer.write_timedelta_value("workDuration", self.work_duration)
        writer.write_date_value("birthDay", self.birthday)
        writer.write_time_value("startWorkTime", self.start_work_time)
        writer.write_time_value("endWorkTime", self.end_work_time)
        writer.write_datetime_value("createdDateTime", self.created_date_time)
        writer.write_str_value("officeLocation", self.office_location)
        writer.write_additional_data_value(self.additional_data)
        
    __test__ = False
        