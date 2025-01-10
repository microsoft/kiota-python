# ------------------------------------
# Copyright (c) Microsoft Corporation. All Rights Reserved.
# Licensed under the MIT License.
# See License in the project root for license information.
# ------------------------------------
from __future__ import annotations

import io
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Generic, Optional, TypeVar

from .serialization import Parsable

if TYPE_CHECKING:
    from .request_adapter import RequestAdapter
    from .serialization import ParseNode, SerializationWriter

T = TypeVar("T")


@dataclass
class MultipartBody(Parsable, Generic[T]):
    """Represents a multipart body for a request or a response.
    Example usage:
        multipart = MultipartBody()
        multipart.add_or_replace_part(
            "file", "image/jpeg", open("image.jpg", "rb").read(), "image.jpg"
        )
        multipart.add_or_replace_part("text", "text/plain", "Hello, World!")
        with open("output.txt", "w") as output_file:
            multipart.serialize(output_file)
    """
    boundary: str = str(uuid.uuid4())
    parts: dict[str, tuple[str, Any, Optional[str]]] = field(default_factory=dict)
    request_adapter: Optional[RequestAdapter] = None

    def add_or_replace_part(
        self,
        part_name: str,
        content_type: str,
        part_value: T,
        filename: Optional[str] = None
    ) -> None:
        """Adds or replaces a part to the multipart body.

        Args:
            part_name (str): The name of the part to add or replace.
            content_type (str): The content type of the part.
            part_value (T): The value of the part.
            filename (str, optional): The filename of the part.

        Returns:
            None
        """
        if not part_name:
            raise ValueError("Part name cannot be null")
        if not content_type:
            raise ValueError("Content type cannot be null")
        if not part_value:
            raise ValueError("Part value cannot be null")
        value: tuple[str, Any, Optional[str]] = (content_type, part_value, filename)
        self.parts[self._normalize_part_name(part_name)] = value

    def get_part_value(self, part_name: str) -> Optional[T]:
        """Gets the value of a part from the multipart body."""
        if not part_name:
            raise ValueError("Part name cannot be null")
        value = self.parts.get(self._normalize_part_name(part_name))
        return value[1] if value else None

    def remove_part(self, part_name: str) -> bool:
        """Removes a part from the multipart body.

        Args:
            part_name (str): The name of the part to remove.

        Returns:
            bool: True if the part was removed, False otherwise.
        """
        if not part_name:
            raise ValueError("Part name cannot be null")
        return self.parts.pop(self._normalize_part_name(part_name), None) is not None

    def get_field_deserializers(self) -> dict[str, Callable[[ParseNode], None]]:
        """Gets the deserialization information for this object.

        Returns:
            dict[str, Callable[[ParseNode], None]]: The deserialization information for this
            object where each entry is a property key with its deserialization callback.
        """
        raise NotImplementedError()

    def serialize(self, writer: SerializationWriter) -> None:
        """Writes the objects properties to the current writer.

        Args:
            writer (SerializationWriter): The writer to write to.
        """
        if not writer:
            raise ValueError("Serialization writer cannot be null")
        if not self.request_adapter or not self.request_adapter.get_serialization_writer_factory():
            raise ValueError("Request adapter or serialization writer factory cannot be null")
        if not self.parts:
            raise ValueError("No parts to serialize")

        first = True
        for part_name, part_value in self.parts.items():
            if first:
                first = False
            else:
                self._add_new_line(writer)

            writer.write_str_value("", f"--{self.boundary}")
            writer.write_str_value("Content-Type", f"{part_value[0]}")
            writer.write_str_value(
                "Content-Disposition", self._get_comtent_disposition(part_name, part_value)
            )
            self._add_new_line(writer)

            if isinstance(part_value[1], Parsable):
                self._write_parsable(writer, part_value)
            elif isinstance(part_value[1], str):
                writer.write_str_value("", part_value[1])
            elif isinstance(part_value[1], bytes):
                writer.write_bytes_value("", part_value[1])
            elif isinstance(part_value[1], io.IOBase):
                writer.write_bytes_value("", part_value[1].read())
            else:
                raise ValueError(f"Unsupported type {type(part_value[1])} for part {part_name}")

        self._add_new_line(writer)
        writer.write_str_value("", f"--{self.boundary}--")

    def _normalize_part_name(self, original: str) -> str:
        return original.lower()

    def _add_new_line(self, writer: SerializationWriter) -> None:
        writer.write_str_value("", "")

    def _get_comtent_disposition(
        self, part_name: str, part_value: tuple[str, Any, Optional[str]]
    ) -> str:
        if len(part_value) >= 3 and part_value[2] is not None:
            return f'form-data; name="{part_name}"; filename="{part_value[2]}"'
        return f'form-data; name="{part_name}"'

    def _write_parsable(self, writer, part_value) -> None:
        if not self.request_adapter or not self.request_adapter.get_serialization_writer_factory():
            raise ValueError("Request adapter or serialization writer factory cannot be null")
        part_writer = (
            self.request_adapter.get_serialization_writer_factory().get_serialization_writer(
                part_value[0]
            )
        )
        part_writer.write_object_value("", part_value[1], None)
        part_content = part_writer.get_serialized_content()
        if hasattr(part_content, "seek"):  # seekable
            part_content.seek(0)
            writer.write_bytes_value("", part_content.read())  #type: ignore
        else:
            writer.write_bytes_value("", part_content)
