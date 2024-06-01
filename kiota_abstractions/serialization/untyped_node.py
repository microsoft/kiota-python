from collections import defaultdict
from parsable import Parsable
from typing import TYPE_CHECKING, Callable, Dict

if TYPE_CHECKING:
    from .parse_node import ParseNode
    from .serialization_writer import SerializationWriter

class UntypedNode(Parsable):
    """
    Base class for untyped node.
    """

    __field_deserializers: Dict[str, Callable[['ParseNode'], None]] = {}

    def get_field_deserializers(self) -> Dict[str, Callable[['ParseNode'], None]]:
        """
        The deserialization information for the current model
        """
        return UntypedNode.__field_deserializers

    def serialize(self, writer: 'SerializationWriter'):
        """
        Serializes information about the current object.

        Args:
            writer (SerializationWriter): Serialization writer to use to serialize this model.
        """
        if not writer:
            raise ValueError("writer cannot be None")

    @staticmethod
    def create_from_discriminator_value(parse_node: 'Parsable'):
        """
        Creates a new instance of the appropriate class based on discriminator value
        
        Args:
            parse_node (ParseNode): The parse node to use to read the discriminator value and create the object
        """
        if not parse_node:
            raise ValueError("parse_node cannot be None")
        return UntypedNode()

    def get_value(self):
        """
        Gets the value of the current node.

        Returns:
            The value assigned to untyped node.
        """
        raise NotImplementedError("This method is not implemented")