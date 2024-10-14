from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Callable, Dict, List, Optional, TypeVar

from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter

T = TypeVar('T')


@dataclass
class User2(Parsable):
    additional_data: Dict[str, Any] = field(default_factory=dict)
    id: Optional[int] = None
    display_name: Optional[str] = None
    age: Optional[int] = None
    gpa: Optional[float] = None

    @staticmethod
    def create_from_discriminator_value(parse_node: Optional[ParseNode] = None) -> User2:
        """
        Creates a new instance of the appropriate class based on discriminator value
        Args:
            parseNode: The parse node to use to read the discriminator value and create the object
        Returns: Attachment
        """
        if not parse_node:
            raise TypeError("parse_node cannot be null")
        return User2()

    def get_field_deserializers(self) -> Dict[str, Callable[[ParseNode], None]]:
        """Gets the deserialization information for this object.

        Returns:
            Dict[str, Callable[[ParseNode], None]]: The deserialization information for this
            object where each entry is a property key with its deserialization callback.
        """
        return {
            "id": lambda n: setattr(self, 'id', n.get_int_value()),
            "display_name": lambda n: setattr(self, 'display_name', n.get_str_value()),
            "age": lambda n: setattr(self, 'age', n.get_int_value()),
            "gpa": lambda n: setattr(self, 'gpa', n.get_float_value())
        }

    def serialize(self, writer: SerializationWriter) -> None:
        """Writes the objects properties to the current writer.

        Args:
            writer (SerializationWriter): The writer to write to.
        """
        if not writer:
            raise TypeError("Writer cannot be null")
        writer.write_int_value("id", self.id)
        writer.write_str_value("display_name", self.display_name)
        writer.write_int_value("age", self.age)
        writer.write_float_value("gpa", self.gpa)
