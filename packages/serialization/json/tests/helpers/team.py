from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Callable
from typing import Optional

from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter

from .user import User


@dataclass
class Team(Parsable):
    lead: Optional[User] = None

    @staticmethod
    def create_from_discriminator_value(parse_node: Optional[ParseNode] = None) -> Team:
        return Team()

    def get_field_deserializers(self) -> dict[str, Callable[[ParseNode], None]]:
        return {"lead": lambda n: setattr(self, 'lead', n.get_object_value(User))}

    def serialize(self, writer: SerializationWriter) -> None:
        writer.write_object_value("lead", self.lead)
