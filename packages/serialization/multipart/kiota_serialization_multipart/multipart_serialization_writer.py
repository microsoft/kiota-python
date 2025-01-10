from __future__ import annotations

import io
from collections.abc import Callable
from datetime import date, datetime, time, timedelta
from enum import Enum
from typing import Any, Optional, TypeVar
from uuid import UUID

from kiota_abstractions.multipart_body import MultipartBody
from kiota_abstractions.serialization import Parsable, SerializationWriter

T = TypeVar("T")
U = TypeVar("U", bound=Parsable)
K = TypeVar("K", bound=Enum)


class MultipartSerializationWriter(SerializationWriter):

    def __init__(self) -> None:

        self._stream: io.BytesIO = io.BytesIO()
        self.writer = io.TextIOWrapper(
            buffer=self._stream,
            encoding='utf-8',
            line_buffering=True,  # Set AutoFlush to True
            newline="\r\n"  # Set NewLine to "\r\n" as per HTTP spec
        )

        self._on_start_object_serialization: Optional[Callable[[Parsable, SerializationWriter],
                                                               None]] = None
        self._on_before_object_serialization: Optional[Callable[[Parsable], None]] = None
        self._on_after_object_serialization: Optional[Callable[[Parsable], None]] = None

    def write_str_value(self, key: Optional[str], value: Optional[str]) -> None:
        """Writes the specified string value to the stream with an optional given key.
        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            value (Optional[str]): The string value to be written.
        """
        if key:
            self.writer.write(key)
        if value:
            if key:
                self.writer.write(": ")
            self.writer.write(value)
        self.writer.write("\n")

    def write_bool_value(self, key: Optional[str], value: Optional[bool]) -> None:
        """Writes the specified boolean value to the stream with an optional given key.
        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            value (Optional[bool]): The boolean value to be written.
        """
        raise NotImplementedError()

    def write_int_value(self, key: Optional[str], value: Optional[int]) -> None:
        """Writes the specified integer value to the stream with an optional given key.
        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            value (Optional[int]): The integer value to be written.
        """
        raise NotImplementedError()

    def write_float_value(self, key: Optional[str], value: Optional[float]) -> None:
        """Writes the specified float value to the stream with an optional given key.
        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            value (Optional[float]): The float value to be written.
        """
        raise NotImplementedError()

    def write_uuid_value(self, key: Optional[str], value: Optional[UUID]) -> None:
        """Writes the specified uuid value to the stream with an optional given key.
        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            value (Optional[UUId]): The uuid value to be written.
        """
        raise NotImplementedError()

    def write_datetime_value(self, key: Optional[str], value: Optional[datetime]) -> None:
        """Writes the specified datetime offset value to the stream with an optional given key.
        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            value (Optional[datetime]): The datetime offset value to be written.
        """
        raise NotImplementedError()

    def write_timedelta_value(self, key: Optional[str], value: Optional[timedelta]) -> None:
        """Writes the specified timedelta value to the stream with an optional given key.
        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            value (Optional[timedelta]): The timedelta value to be written.
        """
        raise NotImplementedError()

    def write_date_value(self, key: Optional[str], value: Optional[date]) -> None:
        """Writes the specified date value to the stream with an optional given key.
        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            value (Optional[date]): The date value to be written.
        """
        raise NotImplementedError()

    def write_time_value(self, key: Optional[str], value: Optional[time]) -> None:
        """Writes the specified time value to the stream with an optional given key.
        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            value (Optional[time]): The time value to be written.
        """
        raise NotImplementedError()

    def write_bytes_value(self, key: Optional[str], value: Optional[bytes]) -> None:
        """Writes the specified byte array as a base64 string to the stream with an optional
        given key.
        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            value (bytes): The byte array to be written.
        """
        if value and len(value) > 0:
            self._stream.write(value)

    def write_collection_of_primitive_values(
        self, key: Optional[str], values: Optional[list[T]]
    ) -> None:
        """Writes the specified collection of primitive values to the stream with an optional
        given key.
        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            values (Optional[list[T]]): The collection of primitive values to be written.
        """
        raise NotImplementedError()

    def write_collection_of_enum_values(
        self, key: Optional[str], values: Optional[list[K]]
    ) -> None:
        """Writes the specified collection of enum values to the stream with an optional given key.
        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            values Optional[list[K]): The enum values to be written.
        """
        raise NotImplementedError()

    def write_enum_value(self, key: Optional[str], value: Optional[K]) -> None:
        """Writes the specified enum value to the stream with an optional given key.
        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            value (Optional[Enum]): The enum value to be written.
        """
        raise NotImplementedError()

    def write_collection_of_object_values(
        self, key: Optional[str], values: Optional[list[U]]
    ) -> None:
        """Writes the specified collection of model objects to the stream with an optional
        given key.
        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            values (Optional[list[U]]): The collection of model objects to be written.
        """
        raise NotImplementedError()

    def write_object_value(
        self, key: Optional[str], value: Optional[U], *additional_values_to_merge: Optional[U]
    ) -> None:
        """Writes the specified model object to the stream with an optional given key.
        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            value (Parsable): The model object to be written.
            additional_values_to_merge (tuple[Parsable]): The additional values to merge to the
            main value when serializing an intersection wrapper.
        """
        temp_writer = self._create_new_writer()

        if not isinstance(value, MultipartBody):
            raise ValueError(f"Expected a MultipartBody instance but got {type(value)}")
        self._serialize_value(self, value)
        if self._on_after_object_serialization:
            self._on_after_object_serialization(value)

    def write_null_value(self, key: Optional[str]) -> None:
        """Writes a null value for the specified key.
        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
        """
        raise NotImplementedError()

    def write_additional_data_value(self, value: dict[str, Any]) -> None:
        """Writes the specified additional data to the stream.
        Args:
            value (dict[str, Any]): he additional data to be written.
        """
        raise NotImplementedError()

    def get_serialized_content(self) -> bytes:
        """Gets the value of the serialized content.
        Returns:
            bytes: The value of the serialized content.
        """
        if self.writer:
            self.writer.flush()
        self._stream.seek(0)
        return self._stream.read()

    @property
    def on_before_object_serialization(self) -> Optional[Callable[[Parsable], None]]:
        """Gets the callback called before the object gets serialized.
        Returns:
            Optional[Callable[[Parsable], None]]:the callback called before the object
            gets serialized.
        """
        return self._on_before_object_serialization

    @on_before_object_serialization.setter
    def on_before_object_serialization(self, value: Optional[Callable[[Parsable], None]]) -> None:
        """Sets the callback called before the objects gets serialized.
        Args:
            value (Optional[Callable[[Parsable], None]]): the callback called before the objects
            gets serialized.
        """
        self._on_before_object_serialization = value

    @property
    def on_after_object_serialization(self) -> Optional[Callable[[Parsable], None]]:
        """Gets the callback called after the object gets serialized.
        Returns:
            Optional[Optional[Callable[[Parsable], None]]]: the callback called after the object
            gets serialized.
        """
        return self._on_after_object_serialization

    @on_after_object_serialization.setter
    def on_after_object_serialization(self, value: Optional[Callable[[Parsable], None]]) -> None:
        """Sets the callback called after the objects gets serialized.
        Args:
            value (Optional[Callable[[Parsable], None]]): the callback called after the objects
            gets serialized.
        """
        self._on_after_object_serialization = value

    @property
    def on_start_object_serialization(
        self
    ) -> Optional[Callable[[Parsable, SerializationWriter], None]]:
        """Gets the callback called right after the serialization process starts.
        Returns:
            Optional[Callable[[Parsable, SerializationWriter], None]]: the callback called
            right after the serialization process starts.
        """
        return self._on_start_object_serialization

    @on_start_object_serialization.setter
    def on_start_object_serialization(
        self, value: Optional[Callable[[Parsable, SerializationWriter], None]]
    ) -> None:
        """Sets the callback called right after the serialization process starts.
        Args:
            value (Optional[Callable[[Parsable, SerializationWriter], None]]): the callback
            called right after the serialization process starts.
        """
        self._on_start_object_serialization = value

    def _serialize_value(self, temp_writer: MultipartSerializationWriter, value: U):
        if on_before := self.on_before_object_serialization:
            on_before(value)
        if on_start := self.on_start_object_serialization:
            on_start(value, self)

        value.serialize(temp_writer)

    def _create_new_writer(self) -> SerializationWriter:
        writer = MultipartSerializationWriter()
        writer.on_before_object_serialization = self.on_before_object_serialization
        writer.on_after_object_serialization = self.on_after_object_serialization
        writer.on_start_object_serialization = self.on_start_object_serialization
        return writer
