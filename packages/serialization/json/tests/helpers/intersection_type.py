from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from kiota_abstractions.serialization import (
    AdditionalDataHolder,
    Parsable,
    ParseNode,
    SerializationWriter,
)
from kiota_abstractions.serialization.parse_node_helper import ParseNodeHelper

from . import User, User2


@dataclass
class InterSectionType(AdditionalDataHolder, Parsable):
    additional_data: Dict[str, Any] = field(default_factory=dict)
    composed_type1: Optional[User] = None
    composed_type2: Optional[User2] = None
    string_value: Optional[str] = None
    composed_type3: Optional[List[User]] = None

    @staticmethod
    def create_from_discriminator_value(parse_node: Optional[ParseNode] = None) -> InterSectionType:
        """
        Creates a new instance of the appropriate class based on discriminator value
        Args:
            parseNode: The parse node to use to read the discriminator value and create the object
        Returns: Attachment
        """
        if not parse_node:
            raise TypeError("parse_node cannot be null")

        result = InterSectionType()
        if string_value := parse_node.get_str_value():
            result.string_value = string_value
        elif values := parse_node.get_collection_of_object_values(User):
            result.composed_type3 = values
        else:
            result.composed_type1 = User()
            result.composed_type2 = User2()

        return result

    def get_field_deserializers(self) -> Dict[str, Callable[[ParseNode], None]]:
        """Gets the deserialization information for this object.

        Returns:
            Dict[str, Callable[[ParseNode], None]]: The deserialization information for this
            object where each entry is a property key with its deserialization callback.
        """
        if self.composed_type1 or self.composed_type2:
            return ParseNodeHelper.merge_deserializers_for_intersection_wrapper(
                self.composed_type1, self.composed_type2
            )
        return {}

    def serialize(self, writer: SerializationWriter) -> None:
        """Writes the objects properties to the current writer.

        Args:
            writer (SerializationWriter): The writer to write to.
        """
        if not writer:
            raise TypeError("Writer cannot be null")
        if self.string_value:
            writer.write_str_value(None, self.string_value)
        elif self.composed_type3:
            writer.write_collection_of_object_values(None, self.composed_type3)
        else:
            writer.write_object_value(None, self.composed_type1, self.composed_type2)
