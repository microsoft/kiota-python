from dataclasses import asdict, dataclass
from json import dumps
from typing import TYPE_CHECKING, Any, Callable, Dict, Protocol, TypeVar

T = TypeVar("T")

if TYPE_CHECKING:
    from .parse_node import ParseNode
    from .serialization_writer import SerializationWriter


@dataclass
class Parsable(Protocol):
    """
    Defines a serializable model object.
    """

    def to_dict(self):
        return asdict(self)

    def to_json(self):
        return dumps(asdict(self), default=str)

    def get_field_deserializers(self) -> Dict[str, Callable[['ParseNode'], None]]:
        """Gets the deserialization information for this object.

        Returns:
            Dict[str, Callable[[ParseNode], None]]: The deserialization information for this
            object where each entry is a property key with its deserialization callback.
        """
        ...

    def serialize(self, writer: 'SerializationWriter') -> None:
        """Writes the objects properties to the current writer.

        Args:
            writer (SerializationWriter): The writer to write to.
        """
        ...
