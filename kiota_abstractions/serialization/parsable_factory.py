from abc import abstractmethod
from typing import Optional

from .parsable import Parsable
from .parse_node import ParseNode


class ParsableFactory(Parsable):
    """Defines the factory for creating parsable objects.
    """

    @staticmethod
    @abstractmethod
    def create_from_discriminator_value(parse_node: Optional[ParseNode]) -> Parsable:
        """Create a new parsable object from the given serialized data.

        Args:
            parse_node (Optional[ParseNode]): The node to parse to get the discriminator value
            from the payload.

        Returns:
            U: The parsable object.
        """
        pass
