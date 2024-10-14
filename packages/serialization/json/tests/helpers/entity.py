from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Optional
from uuid import UUID

from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter


@dataclass
class Entity(Parsable):

    id: Optional[UUID] = None

    @staticmethod
    def create_from_discriminator_value(parse_node: Optional[ParseNode] = None) -> Entity:
        """
        Creates a new instance of the appropriate class based on discriminator value
        Args:
            parseNode: The parse node to use to read the discriminator value and create the object
        Returns: Attachment
        """
        if not parse_node:
            raise ValueError("parse_node cannot be undefined")
        return Entity()

    def get_field_deserializers(self) -> Dict[str, Callable[[ParseNode], None]]:
        """Gets the deserialization information for this object.

        Returns:
            Dict[str, Callable[[ParseNode], None]]: The deserialization information for this
            object where each entry is a property key with its deserialization callback.
        """
        return {
            "id": lambda n: setattr(self, 'id', n.get_uuid_value()),
        }

    def serialize(self, writer: SerializationWriter) -> None:
        """Writes the objects properties to the current writer.

        Args:
            writer (SerializationWriter): The writer to write to.
        """
        if not writer:
            raise ValueError("Writer cannot be undefined")
        writer.write_uuid_value("id", self.id)
