from abc import abstractmethod
from typing import Generic, Optional, Protocol, TypeVar

from .parsable import Parsable
from .parse_node import ParseNode

U_co = TypeVar("U_co", bound="Parsable", covariant=True)


class ParsableFactory(Protocol, Generic[U_co]):
    """Defines the factory for creating parsable objects.
    """

    @staticmethod
    @abstractmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> U_co:
        """Create a new parsable object from the given serialized data.

        Args:
            parse_node (Optional[ParseNode]): The node to parse to get the discriminator value
            from the payload.

        Returns:
            U: The parsable object.
        """
        pass
