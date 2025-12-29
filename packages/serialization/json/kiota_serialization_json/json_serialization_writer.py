from __future__ import annotations

import base64
import json
from collections.abc import Callable
from datetime import date, datetime, time, timedelta
from enum import Enum
from typing import Any, Optional, TypeVar
from uuid import UUID

from kiota_abstractions.date_utils import parse_timedelta_string
from kiota_abstractions.serialization import Parsable, SerializationWriter

T = TypeVar("T")
U = TypeVar("U", bound=Parsable)
K = TypeVar("K", bound=Enum)
PRIMITIVE_TYPES = [bool, str, int, float, UUID, datetime, timedelta, date, time, bytes, Enum]
PRIMITIVE_TYPES_WITH_NONE = PRIMITIVE_TYPES + [type(None)]


class JsonSerializationWriter(SerializationWriter):

    PROPERTY_SEPARATOR: str = ','

    def __init__(self) -> None:
        self.writer: dict = {}
        self.value: Any = None

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
        if isinstance(value, str):
            if key:
                self.writer[key] = value
            else:
                self.value = value

    def write_bool_value(self, key: Optional[str], value: Optional[bool]) -> None:
        """Writes the specified boolean value to the stream with an optional given key.
        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            value (Optional[bool]): The boolean value to be written.
        """
        if isinstance(value, bool):
            if key:
                self.writer[key] = value
            else:
                self.value = value

    def write_int_value(self, key: Optional[str], value: Optional[int]) -> None:
        """Writes the specified integer value to the stream with an optional given key.
        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            value (Optional[int]): The integer value to be written.
        """
        if isinstance(value, int):
            if key:
                self.writer[key] = value
            else:
                self.value = value

    def write_float_value(self, key: Optional[str], value: Optional[float]) -> None:
        """Writes the specified float value to the stream with an optional given key.
        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            value (Optional[float]): The float value to be written.
        """
        if isinstance(value, (float, int)):
            if key:
                self.writer[key] = float(value)
            else:
                self.value = float(value)

    def write_uuid_value(self, key: Optional[str], value: Optional[UUID]) -> None:
        """Writes the specified uuid value to the stream with an optional given key.
        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            value (Optional[UUID]): The uuid value to be written.
        """
        if isinstance(value, UUID):
            if key:
                self.writer[key] = str(value)
            else:
                self.value = str(value)
        elif isinstance(value, str):
            try:
                UUID(value)
                if key:
                    self.writer[key] = value
                else:
                    self.value = value
            except ValueError:
                if key:
                    raise ValueError(f"Invalid UUID string value found for property {key}")
                raise ValueError("Invalid UUID string value found")

    def write_datetime_value(self, key: Optional[str], value: Optional[datetime]) -> None:
        """Writes the specified datetime offset value to the stream with an optional given key.
        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            value (Optional[datetime]): The datetime offset value to be written.
        """
        if isinstance(value, datetime):
            if key:
                self.writer[key] = value.isoformat()
            else:
                self.value = value.isoformat()
        elif isinstance(value, str):
            try:
                datetime.fromisoformat(value)
                if key:
                    self.writer[key] = value
                else:
                    self.value = value
            except ValueError:
                if key:
                    raise ValueError(f"Invalid datetime string value found for property {key}")
                raise ValueError("Invalid datetime string value found")

    def write_timedelta_value(self, key: Optional[str], value: Optional[timedelta]) -> None:
        """Writes the specified timedelta value to the stream with an optional given key.
        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            value (Optional[timedelta]): The timedelta value to be written.
        """
        if isinstance(value, timedelta):
            if key:
                self.writer[key] = str(value)
            else:
                self.value = str(value)
        elif isinstance(value, str):
            try:
                parse_timedelta_string(value)
                if key:
                    self.writer[key] = value
                else:
                    self.value = value
            except ValueError:
                if key:
                    raise ValueError(f"Invalid timedelta string value found for property {key}")
                raise ValueError("Invalid timedelta string value found")

    def write_date_value(self, key: Optional[str], value: Optional[date]) -> None:
        """Writes the specified date value to the stream with an optional given key.
        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            value (Optional[date]): The date value to be written.
        """
        if isinstance(value, date):
            if key:
                self.writer[key] = str(value)
            else:
                self.value = str(value)
        elif isinstance(value, str):
            try:
                date.fromisoformat(value)
                if key:
                    self.writer[key] = value
                else:
                    self.value = value
            except ValueError:
                if key:
                    raise ValueError(f"Invalid date string value found for property {key}")
                raise ValueError("Invalid date string value found")

    def write_time_value(self, key: Optional[str], value: Optional[time]) -> None:
        """Writes the specified time value to the stream with an optional given key.
        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            value (Optional[time]): The time value to be written.
        """
        if isinstance(value, time):
            if key:
                self.writer[key] = str(value)
            else:
                self.value = str(value)
        elif isinstance(value, str):
            try:
                time.fromisoformat(value)
                if key:
                    self.writer[key] = value
                else:
                    self.value = value
            except ValueError:
                if key:
                    raise ValueError(f"Invalid time string value found for property {key}")
                raise ValueError("Invalid time string value found")

    def write_collection_of_primitive_values(
        self, key: Optional[str], values: Optional[list[T]]
    ) -> None:
        """Writes the specified collection of primitive values to the stream with an optional
        given key.
        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            values (Optional[list[T]]): The collection of primitive values to be written.
        """
        if isinstance(values, list):
            result = []
            for val in values:
                temp_writer: JsonSerializationWriter = self._create_new_writer()
                temp_writer.write_any_value(None, val)
                result.append(temp_writer.value)

            if key:
                self.writer[key] = result
            else:
                self.value = result

    def write_collection_of_object_values(
        self, key: Optional[str], values: Optional[list[U]]
    ) -> None:
        """Writes the specified collection of model objects to the stream with an optional
        given key.
        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            values (Optional[list[U]]): The collection of model objects to be written.
        """
        if isinstance(values, list):
            obj_list = []
            for val in values:
                temp_writer = self._create_new_writer()
                temp_writer.write_object_value(None, val)
                obj_list.append(temp_writer.value)

            if key:
                self.writer[key] = obj_list
            else:
                self.value = obj_list

    def write_collection_of_enum_values(
        self, key: Optional[str], values: Optional[list[K]]
    ) -> None:
        """Writes the specified collection of enum values to the stream with an optional given key.
        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            values (Optional[list[K]]): The enum values to be written.
        """
        if isinstance(values, list):
            result = []
            for val in values:
                temp_writer = self._create_new_writer()
                temp_writer.write_enum_value(None, val)
                result.append(temp_writer.value)

            if key:
                self.writer[key] = result
            else:
                self.value = result

    def __write_collection_of_dict_values(
        self, key: Optional[str], values: Optional[list[dict[str, Any]]]
    ) -> None:
        """Writes the specified collection of dictionary values to the stream with an optional
            given key.
        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            values (Optional[list[dict[str, Any]]]): The collection of dictionary values
            to be written.
        """
        if isinstance(values, list):
            result = []
            for val in values:
                temp_writer: JsonSerializationWriter = self._create_new_writer()
                temp_writer.__write_dict_value(None, val)
                result.append(temp_writer.value)

            if key:
                self.writer[key] = result
            else:
                self.value = result

    def write_bytes_value(self, key: Optional[str], value: Optional[bytes]) -> None:
        """Writes the specified byte array as a base64 string to the stream with an optional
        given key.
        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            value (bytes): The byte array to be written.
        """
        if isinstance(value, bytes):
            base64_bytes = base64.b64encode(value)
            base64_string = base64_bytes.decode('utf-8')
            if key:
                self.writer[key] = base64_string
            else:
                self.value = base64_string

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
        if value or additional_values_to_merge:
            temp_writer = self._create_new_writer()

            if value:
                self._serialize_value(temp_writer, value)

            if additional_values_to_merge:
                for additional_value in filter(lambda x: x is not None, additional_values_to_merge):
                    self._serialize_value(temp_writer, additional_value)  # type: ignore
                    if on_after := self.on_after_object_serialization:
                        on_after(additional_value)  # type: ignore

            if value and self._on_after_object_serialization:
                self._on_after_object_serialization(value)

            # Use temp_writer.value if available (for composed types like oneOf wrappers),
            # otherwise fall back to temp_writer.writer (for regular objects with properties)
            serialized_value = (
                temp_writer.value if temp_writer.value is not None else temp_writer.writer
            )
            if key:
                self.writer[key] = serialized_value
            else:
                self.value = serialized_value

    def write_enum_value(self, key: Optional[str], value: Optional[K]) -> None:
        """Writes the specified enum value to the stream with an optional given key.
        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            value (Optional[K]): The enum value to be written.
        """
        if isinstance(value, Enum):
            if key:
                self.writer[key] = value.value
            else:
                self.value = value.value

    def write_null_value(self, key: Optional[str]) -> None:
        """Writes a null value for the specified key.
        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
        """
        if key:
            self.writer[key] = None
        else:
            self.value = None

    def __write_dict_value(self, key: Optional[str], value: dict[str, Any]) -> None:
        """Writes the specified dictionary value to the stream with an optional given key.
        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            value (dict[str, Any]): The dictionary value to be written.
        """
        if isinstance(value, dict):
            temp_writer: JsonSerializationWriter = self._create_new_writer()
            for dict_key, dict_value in value.items():
                temp_writer.write_any_value(dict_key, dict_value)
            if key:
                self.writer[key] = temp_writer.writer
            else:
                self.value = temp_writer.writer

    def write_additional_data_value(self, value: dict[str, Any]) -> None:
        """Writes the specified additional data to the stream.
        Args:
            value (dict[str, Any]): The additional data to be written.
        """
        if isinstance(value, dict):
            for key, val in value.items():
                self.write_any_value(key, val)

    def get_serialized_content(self) -> bytes:
        """Gets the value of the serialized content.
        Returns:
            bytes: The value of the serialized content.
        """
        if self.writer and self.value:
            # Json output is invalid if it has a mix of values
            # and key-value pairs.
            raise ValueError("Invalid Json output")

        if self.value:
            json_string = json.dumps(self.value)
            self.value = None
        else:
            json_string = json.dumps(self.writer)
            self.writer.clear()

        stream = json_string.encode('utf-8')
        return stream

    @property
    def on_before_object_serialization(self) -> Optional[Callable[[Parsable], None]]:
        """Gets the callback called before the object gets serialized.
        Returns:
            Optional[Callable[[Parsable], None]]: The callback called before the object
            gets serialized.
        """
        return self._on_before_object_serialization

    @on_before_object_serialization.setter
    def on_before_object_serialization(self, value: Optional[Callable[[Parsable], None]]) -> None:
        """Sets the callback called before the objects get serialized.
        Args:
            value (Optional[Callable[[Parsable], None]]): The callback called before the objects
            get serialized.
        """
        self._on_before_object_serialization = value

    @property
    def on_after_object_serialization(self) -> Optional[Callable[[Parsable], None]]:
        """Gets the callback called after the object gets serialized.
        Returns:
            Optional[Optional[Callable[[Parsable], None]]]: The callback called after the object
            gets serialized.
        """
        return self._on_after_object_serialization

    @on_after_object_serialization.setter
    def on_after_object_serialization(self, value: Optional[Callable[[Parsable], None]]) -> None:
        """Sets the callback called after the objects get serialized.
        Args:
            value (Optional[Callable[[Parsable], None]]): The callback called after the objects
            get serialized.
        """
        self._on_after_object_serialization = value

    @property
    def on_start_object_serialization(
        self
    ) -> Optional[Callable[[Parsable, SerializationWriter], None]]:
        """Gets the callback called right after the serialization process starts.
        Returns:
            Optional[Callable[[Parsable, SerializationWriter], None]]: The callback called
            right after the serialization process starts.
        """
        return self._on_start_object_serialization

    @on_start_object_serialization.setter
    def on_start_object_serialization(
        self, value: Optional[Callable[[Parsable, SerializationWriter], None]]
    ) -> None:
        """Sets the callback called right after the serialization process starts.
        Args:
            value (Optional[Callable[[Parsable, SerializationWriter], None]]): The callback
            called right after the serialization process starts.
        """
        self._on_start_object_serialization = value

    def write_non_parsable_object_value(self, key: Optional[str], value: T) -> None:
        """Writes the specified value to the stream with an optional given key.
        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            value (object): The value to be written.
        """
        if hasattr(value, '__dict__'):
            if key:
                self.writer[key] = value.__dict__
            else:
                self.value = value.__dict__

    def write_any_value(self, key: Optional[str], value: Any) -> Any:
        """Writes the specified value to the stream with an optional given key.
        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            value (Any): The value to be written.
        """
        value_type = type(value)
        if value is None:
            self.write_null_value(key)
        elif isinstance(value, Parsable):
            self.write_object_value(key, value)
        elif isinstance(value, list):
            if all(isinstance(x, Parsable) for x in value):
                self.write_collection_of_object_values(key, value)
            elif all(isinstance(x, Enum) for x in value):
                self.write_collection_of_enum_values(key, value)
            elif all(
                any(isinstance(x, primitive_type) for primitive_type in PRIMITIVE_TYPES_WITH_NONE)
                for x in value
            ):
                self.write_collection_of_primitive_values(key, value)
            elif all(isinstance(x, dict) for x in value):
                self.__write_collection_of_dict_values(key, value)
            else:
                raise TypeError(
                    f"Encountered an unknown collection type during serialization {type(value)}\
                    with key {key}"
                )
        elif isinstance(value, dict):
            self.__write_dict_value(key, value)
        else:
            for primitive_type in PRIMITIVE_TYPES:
                if isinstance(value, primitive_type):
                    method = getattr(self, f"write_{primitive_type.__name__.lower()}_value")
                    method(key, value)
                    return
            if hasattr(value, "__dict__"):
                self.write_non_parsable_object_value(key, value)
            else:
                raise TypeError(
                    f"Encountered an unknown type during serialization {type(value)} with key {key}"
                )

    def _serialize_value(self, temp_writer: JsonSerializationWriter, value: U):
        if on_before := self.on_before_object_serialization:
            on_before(value)
        if on_start := self.on_start_object_serialization:
            on_start(value, self)

        value.serialize(temp_writer)

    def _create_new_writer(self) -> JsonSerializationWriter:
        writer = JsonSerializationWriter()
        writer.on_before_object_serialization = self.on_before_object_serialization
        writer.on_after_object_serialization = self.on_after_object_serialization
        writer.on_start_object_serialization = self.on_start_object_serialization
        return writer
