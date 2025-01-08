from __future__ import annotations

import base64
from collections.abc import Callable
from datetime import date, datetime, time, timedelta
from enum import Enum
from typing import Any, Optional, TypeVar
from urllib.parse import quote_plus
from uuid import UUID

from kiota_abstractions.serialization import Parsable, SerializationWriter

T = TypeVar("T")
U = TypeVar("U", bound=Parsable)
K = TypeVar("K", bound=Enum)


class FormSerializationWriter(SerializationWriter):

    def __init__(self) -> None:
        self.writer: str = ""
        self.depth = 0

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
        if key and value:
            if len(self.writer) > 0:
                self.writer += "&"
            self.writer += f"{quote_plus(key.strip())}={quote_plus(value.strip())}"

    def write_bool_value(self, key: Optional[str], value: Optional[bool]) -> None:
        """Writes the specified boolean value to the stream with an optional given key.
        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            value (Optional[bool]): The boolean value to be written.
        """
        if key and (value or value is False):
            self.write_str_value(key, str(value).lower())

    def write_int_value(self, key: Optional[str], value: Optional[int]) -> None:
        """Writes the specified integer value to the stream with an optional given key.
        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            value (Optional[int]): The integer value to be written.
        """
        if key and (value or value == 0):
            self.write_str_value(key, str(value))

    def write_float_value(self, key: Optional[str], value: Optional[float]) -> None:
        """Writes the specified float value to the stream with an optional given key.
        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            value (Optional[float]): The float value to be written.
        """
        if key and (value or value == 0):
            self.write_str_value(key, str(value))

    def write_uuid_value(self, key: Optional[str], value: Optional[UUID]) -> None:
        """Writes the specified uuid value to the stream with an optional given key.
        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            value (Optional[UUId]): The uuid value to be written.
        """
        if key and value:
            self.write_str_value(key, str(value))

    def write_datetime_value(self, key: Optional[str], value: Optional[datetime]) -> None:
        """Writes the specified datetime offset value to the stream with an optional given key.
        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            value (Optional[datetime]): The datetime offset value to be written.
        """
        if key and value:
            if isinstance(value, datetime):
                self.write_str_value(key, str(value.isoformat()))
            else:
                self.write_str_value(key, str(value))

    def write_timedelta_value(self, key: Optional[str], value: Optional[timedelta]) -> None:
        """Writes the specified timedelta value to the stream with an optional given key.
        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            value (Optional[timedelta]): The timedelta value to be written.
        """
        if key and value:
            self.write_str_value(key, str(value))

    def write_date_value(self, key: Optional[str], value: Optional[date]) -> None:
        """Writes the specified date value to the stream with an optional given key.
        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            value (Optional[date]): The date value to be written.
        """
        if key and value:
            self.write_str_value(key, str(value))

    def write_time_value(self, key: Optional[str], value: Optional[time]) -> None:
        """Writes the specified time value to the stream with an optional given key.
        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            value (Optional[time]): The time value to be written.
        """
        if key and value:
            self.write_str_value(key, str(value))

    def write_bytes_value(self, key: Optional[str], value: Optional[bytes]) -> None:
        """Writes the specified byte array as a base64 string to the stream with an optional
        given key.
        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            value (bytes): The byte array to be written.
        """
        if key and isinstance(value, bytes):
            base64_bytes = base64.b64encode(value)
            base64_string = base64_bytes.decode('utf-8')
            self.write_str_value(key, base64_string)

    def write_collection_of_primitive_values(
        self, key: Optional[str], values: Optional[list[T]]
    ) -> None:
        """Writes the specified collection of primitive values to the stream with an optional
        given key.
        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            values (Optional[list[T]]): The collection of primitive values to be written.
        """
        primitive_types = [bool, str, int, float, UUID, datetime, timedelta, date, time, Enum]
        if key and values:
            for val in values:
                if type(val) in primitive_types:
                    method = getattr(self, f'write_{type(val).__name__.lower()}_value')
                    method(key, val)

    def write_collection_of_enum_values(
        self, key: Optional[str], values: Optional[list[K]]
    ) -> None:
        """Writes the specified collection of enum values to the stream with an optional given key.
        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            values Optional[list[K]): The enum values to be written.
        """
        if key and values:
            if isinstance(values, list):
                for val in values:
                    if isinstance(val, Enum):
                        self.write_str_value(key, str(val.value))

    def write_enum_value(self, key: Optional[str], value: Optional[K]) -> None:
        """Writes the specified enum value to the stream with an optional given key.
        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            value (Optional[K]): The enum value to be written.
        """
        if key and value:
            if isinstance(value, Enum):
                self.write_str_value(key, str(value.value))
            if isinstance(value, list):
                values = ",".join([str(val.value) for val in value])
                self.write_str_value(key, values)

    def write_collection_of_object_values(
        self, key: Optional[str], values: Optional[list[U]]
    ) -> None:
        """Writes the specified collection of model objects to the stream with an optional
        given key.
        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            values (Optional[list[U]]): The collection of model objects to be written.
        """
        raise Exception("Form serialization does not support collections.")

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
        if self.depth > 0:
            raise Exception("Form serialization does not support nested objects.")
        self.depth += 1
        temp_writer = self._create_new_writer()

        if value is not None:
            self._serialize_value(temp_writer, value)

        if additional_values_to_merge:
            for additional_value in filter(lambda x: x is not None, additional_values_to_merge):
                self._serialize_value(temp_writer, additional_value)  # type: ignore
                if on_after := self.on_after_object_serialization:
                    on_after(additional_value)  # type: ignore

        if value and self._on_after_object_serialization:
            self._on_after_object_serialization(value)

        if len(self.writer) > 0:
            self.writer += "&"
        self.writer += f"{quote_plus(key.strip()) if key is not None else ''}={temp_writer.writer}"
        self.depth -= 1

    def write_null_value(self, key: Optional[str]) -> None:
        """Writes a null value for the specified key.
        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
        """
        if key:
            self.write_str_value(key, "null")

    def write_additional_data_value(self, value: dict[str, Any]) -> None:
        """Writes the specified additional data to the stream.
        Args:
            value (dict[str, Any]): he additional data to be written.
        """
        if isinstance(value, dict):
            for key, val in value.items():
                if isinstance(val, Parsable):
                    raise Exception("Form serialization does not support nested objects")
                self.write_any_value(key, val)

    def get_serialized_content(self) -> bytes:
        """Gets the value of the serialized content.
        Returns:
            bytes: The value of the serialized content.
        """
        if self.writer:
            return self.writer.encode('utf-8')
        return b''

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

    def write_non_parsable_object_value(self, key: Optional[str], value: T) -> None:
        """Writes the specified value to the stream with an optional given key.
        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            value (object): The value to be written.
        """
        if key and value:
            if hasattr(value, '__dict__'):
                temp_writer = self._create_new_writer()
                for k, v in value.__dict__.items():
                    temp_writer.write_any_value(k, v)
                if len(self.writer) > 0:
                    self.writer += "&"
                self.writer += f"{quote_plus(key.strip())}={temp_writer.writer}"

    def write_any_value(self, key: Optional[str], value: Any) -> Any:
        """Writes the specified value to the stream with an optional given key.
        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            value Any): The value to be written.
        """
        primitive_types = [bool, str, int, float, UUID, datetime, timedelta, date, time, Enum]
        if key and value:
            value_type = type(value)
            if value_type in primitive_types:
                method = getattr(self, f'write_{value_type.__name__.lower()}_value')
                method(key, value)
            elif isinstance(value, list):
                if all(isinstance(x, Enum) for x in value):
                    self.write_collection_of_enum_values(key, value)
                else:
                    self.write_collection_of_primitive_values(key, value)
            elif isinstance(value, Parsable):
                self.write_object_value(key, value)
            elif hasattr(value, '__dict__'):
                self.write_non_parsable_object_value(key, value)
            else:
                raise TypeError(
                    f"Encountered an unknown type during serialization {value_type} \
                        with key {key}"
                )

    def _serialize_value(self, temp_writer: FormSerializationWriter, value: U):
        if on_before := self.on_before_object_serialization:
            on_before(value)
        if on_start := self.on_start_object_serialization:
            on_start(value, self)

        value.serialize(temp_writer)

    def _create_new_writer(self) -> FormSerializationWriter:
        writer = FormSerializationWriter()
        writer.on_before_object_serialization = self.on_before_object_serialization
        writer.on_after_object_serialization = self.on_after_object_serialization
        writer.on_start_object_serialization = self.on_start_object_serialization
        return writer
