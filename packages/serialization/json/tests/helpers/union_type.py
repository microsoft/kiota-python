from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from kiota_abstractions.serialization.parse_node_helper import ParseNodeHelper

from . import User, User2


@dataclass
class UnionType(Parsable):
    additional_data: Dict[str, Any] = field(default_factory=dict)
    composed_type1: Optional[User] = None
    composed_type2: Optional[User2] = None
    string_value: Optional[str] = None
    composed_type3: Optional[List[User]] = None

    @staticmethod
    def create_from_discriminator_value(parse_node: Optional[ParseNode] = None) -> UnionType:
        """
        Creates a new instance of the appropriate class based on discriminator value
        Args:
            parseNode: The parse node to use to read the discriminator value and create the object
        Returns: Attachment
        """
        if not parse_node:
            raise TypeError("parse_node cannot be null")

        try:
            mapping_value = parse_node.get_child_node("@odata.type").get_str_value()
        except AttributeError:
            mapping_value = None
        result = UnionType()
        if mapping_value and mapping_value.casefold() == "#microsoft.graph.User".casefold():
            result.composed_type1 = User()
        elif mapping_value and mapping_value.casefold() == "#microsoft.graph.User2".casefold():
            result.composed_type2 = User2()
        elif string_value := parse_node.get_str_value():
            result.string_value = string_value
        elif values := parse_node.get_collection_of_object_values(User):
            result.composed_type3 = values
        return result

    def get_field_deserializers(self) -> Dict[str, Callable[[ParseNode], None]]:
        """Gets the deserialization information for this object.

        Returns:
            Dict[str, Callable[[ParseNode], None]]: The deserialization information for this
            object where each entry is a property key with its deserialization callback.
        """
        if self.composed_type1:
            return self.composed_type1.get_field_deserializers()
        if self.composed_type2:
            return self.composed_type2.get_field_deserializers()
        # composed_type3 is omitted on purpose
        return {}

    def serialize(self, writer: SerializationWriter) -> None:
        """Writes the objects properties to the current writer.

        Args:
            writer (SerializationWriter): The writer to write to.
        """
        if not writer:
            raise TypeError("Writer cannot be null")

        if self.composed_type1:
            writer.write_object_value(None, self.composed_type1)
        elif self.composed_type2:
            writer.write_object_value(None, self.composed_type2)
        elif self.composed_type3:
            writer.write_collection_of_object_values(None, self.composed_type3)
        elif self.string_value:
            writer.write_str_value(None, self.string_value)
