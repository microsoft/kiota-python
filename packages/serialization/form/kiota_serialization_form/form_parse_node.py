from __future__ import annotations

import warnings
from collections import defaultdict
from collections.abc import Callable
from datetime import date, datetime, time, timedelta
from enum import Enum
from typing import Any, Optional, TypeVar
from urllib.parse import unquote_plus
from uuid import UUID

from kiota_abstractions.date_utils import (
    datetime_from_iso_format_compat,
    parse_timedelta_string,
    time_from_iso_format_compat,
)
from kiota_abstractions.serialization import Parsable, ParsableFactory, ParseNode

T = TypeVar("T", bool, str, int, float, UUID, datetime, timedelta, date, time, bytes)

U = TypeVar("U", bound=Parsable)

K = TypeVar("K", bound=Enum)


class FormParseNode(ParseNode):
    """Represents a parse node that can be used to parse a form url encoded string."""

    def __init__(self, raw_value: str) -> None:
        self._raw_value = raw_value
        self._node = unquote_plus(raw_value)
        self._fields = self._get_fields(raw_value)
        self._on_before_assign_field_values: Optional[Callable[[Parsable], None]] = None
        self._on_after_assign_field_values: Optional[Callable[[Parsable], None]] = None

    def get_str_value(self) -> Optional[str]:
        """Gets the string value from the node
        Returns:
            str: The string value of the node
        """
        return self._get_str_value(self._node)

    def get_bool_value(self) -> Optional[bool]:
        """Gets the boolean value of the node
        Returns:
            bool: The boolean value of the node
        """
        return self._get_bool_value(self._node)

    def get_int_value(self) -> Optional[int]:
        """Gets the integer value of the node
        Returns:
            int: The integer value of the node
        """
        return self._get_int_value(self._node)

    def get_float_value(self) -> Optional[float]:
        """Gets the float value of the node
        Returns:
            float: The integer value of the node
        """
        return self._get_float_value(self._node)

    def get_uuid_value(self) -> Optional[UUID]:
        """Gets the UUID value of the node
        Returns:
            UUID: The GUID value of the node
        """
        return self._get_uuid_value(self._node)

    def get_datetime_value(self) -> Optional[datetime]:
        """Gets the datetime value of the node
        Returns:
            datetime: The datetime value of the node
        """
        return self._get_datetime_value(self._node)

    def get_timedelta_value(self) -> Optional[timedelta]:
        """Gets the timedelta value of the node
        Returns:
            timedelta: The timedelta value of the node
        """
        return self._get_timedelta_value(self._node)

    def get_date_value(self) -> Optional[date]:
        """Gets the date value of the node
        Returns:
            date: The datevalue of the node in terms on year, month, and day.
        """
        return self._get_date_value(self._node)

    def get_time_value(self) -> Optional[time]:
        """Gets the time value of the node
        Returns:
            time: The time value of the node in terms of hour, minute, and second.
        """
        return self._get_time_value(self._node)

    def get_bytes_value(self) -> Optional[bytes]:
        """Get the bytes value of the node
        Returns:
            bytes: The decoded bytes value
        """
        return self._get_bytes_value(self._node)

    def get_child_node(self, field_name: str) -> Optional[ParseNode]:
        """Gets the child node of the node
        Returns:
            Optional[ParseNode]: The child node of the node
        """
        if field_name in self._fields:
            return FormParseNode(self._fields[field_name])
        return None

    def get_collection_of_primitive_values(self, primitive_type: type[T]) -> Optional[list[T]]:
        """Gets the collection of primitive values of the node
        Args:
            primitive_type: The type of primitive to return.
        Returns:
            list[T]: The collection of primitive values
        """
        if not primitive_type:
            raise Exception("Primitive type for deserialization cannot be null")

        converters = {
            bool: self._get_bool_value,
            str: self._get_str_value,
            int: self._get_int_value,
            float: self._get_float_value,
            UUID: self._get_uuid_value,
            datetime: self._get_datetime_value,
            timedelta: self._get_timedelta_value,
            date: self._get_date_value,
            time: self._get_time_value,
            bytes: self._get_bytes_value,
        }
        converter = converters.get(primitive_type)
        if converter is None:
            raise Exception(f"Encountered an unknown type during deserialization {primitive_type}")
        return [
            converter(unquote_plus(item)) for item in self._node.split(',')
        ]  # type: ignore[misc]

    def get_collection_of_object_values(self, factory: ParsableFactory[U]) -> Optional[list[U]]:
        raise Exception("Collection of object values is not supported with uri form encoding.")

    def get_collection_of_enum_values(self, enum_class: K) -> Optional[list[K]]:
        """Gets the collection of enum values of the node
        Returns:
            list[K]: The collection of enum values
        """
        values = self._node.split(',')
        if values:
            return list(
                map(
                    lambda x: self._create_new_node(x).get_enum_value(enum_class),  # type: ignore
                    values
                )
            )
        return []

    def get_enum_value(self, enum_class: K) -> Optional[K]:
        """Gets the enum value of the node
        Returns:
            Optional[K]: The enum value of the node
        """

        if not self._node:
            return None
        enum_values = [e.value for e in enum_class]  # type: ignore
        if self._node in enum_values:
            return enum_class(self._node)  # type: ignore
        values = self._node.split(',')
        if not len(values) > 1:
            raise Exception(f'Invalid value: {self._node} for enum {enum_class}.')
        result = []
        for value in values:
            if value not in enum_values:
                raise Exception(f'Invalid value: {value} for enum {enum_class}.')
            result.append(enum_class(value))  # type: ignore
        return result  # type: ignore

    def get_object_value(self, factory: ParsableFactory[U]) -> U:
        """Gets the model object value of the node
        Returns:
            Parsable: The model object value of the node
        """

        result = factory.create_from_discriminator_value(self)
        if on_before := self.on_before_assign_field_values:
            on_before(result)
        self._assign_field_values(result)
        if on_after := self.on_after_assign_field_values:
            on_after(result)
        return result

    @property
    def on_before_assign_field_values(self) -> Optional[Callable[[Parsable], None]]:
        """Gets the callback called before the node is deserialized.
        Returns:
            Callable[[Parsable], None]: the callback called before the node is deserialized.
        """
        return self._on_before_assign_field_values

    @on_before_assign_field_values.setter
    def on_before_assign_field_values(self, value: Callable[[Parsable], None]) -> None:
        """Sets the callback called before the node is deserialized.
        Args:
            value (Callable[[Parsable], None]): the callback called before the node is
            deserialized.
        """
        self._on_before_assign_field_values = value

    @property
    def on_after_assign_field_values(self) -> Optional[Callable[[Parsable], None]]:
        """Gets the callback called before the node is deserialized.
        Returns:
            Callable[[Parsable], None]: the callback called before the node is deserialized.
        """
        return self._on_after_assign_field_values

    @on_after_assign_field_values.setter
    def on_after_assign_field_values(self, value: Callable[[Parsable], None]) -> None:
        """Sets the callback called after the node is deserialized.
        Args:
            value (Callable[[Parsable], None]): the callback called after the node is
            deserialized.
        """
        self._on_after_assign_field_values = value

    def _assign_field_values(self, item: Parsable) -> None:
        """Assigns the field values to the model object"""

        # if object is null
        if not self._fields:
            return

        item_additional_data = None
        if not hasattr(item, "additional_data") or item.additional_data is None:
            item_additional_data = {}
        else:
            item_additional_data = item.additional_data

        field_deserializers = item.get_field_deserializers()

        for field_name, field_value in self._fields.items():
            if field_name in field_deserializers:
                if field_value is None:
                    continue
                field_deserializer = field_deserializers[field_name]
                field_deserializer(FormParseNode(field_value))
            elif item_additional_data is not None:
                item_additional_data[field_name] = self.try_get_anything(field_value)
            else:
                warnings.warn(
                    f"Found additional property {field_name} to \
                    deserialize but the model doesn't support additional data"
                )

    def try_get_anything(self, value: Any) -> Any:
        if isinstance(value, (int, float, bool)) or value is None:
            return value
        if isinstance(value, list):
            return list(map(self.try_get_anything, value))
        if isinstance(value, dict):
            return dict(map(lambda x: (x[0], self.try_get_anything(x[1])), value.items()))
        if isinstance(value, str):
            try:
                datetime_obj = datetime_from_iso_format_compat(value)
                return datetime_obj
            except ValueError:
                pass
            try:
                return UUID(value)
            except ValueError:
                pass
            try:
                return parse_timedelta_string(value)
            except ValueError:
                pass
            try:
                return date.fromisoformat(value)
            except ValueError:
                pass
            try:
                return time_from_iso_format_compat(value)
            except ValueError:
                pass
            return value
        raise ValueError(f"Unexpected additional value type {type(value)} during deserialization.")

    def _create_new_node(self, node: Any) -> FormParseNode:
        new_node: FormParseNode = FormParseNode(node)
        if self.on_before_assign_field_values:
            new_node.on_before_assign_field_values = self.on_before_assign_field_values
        if self.on_after_assign_field_values:
            new_node.on_after_assign_field_values = self.on_after_assign_field_values
        return new_node

    @staticmethod
    def _get_str_value(value: str) -> Optional[str]:
        if value and value != "null":
            try:
                return str(value)
            except:
                return None
        return None

    @staticmethod
    def _get_bool_value(value: str) -> Optional[bool]:
        if value and value != "null":
            return value.lower() == "true"
        return None

    @staticmethod
    def _get_int_value(value: str) -> Optional[int]:
        if value and value != "null":
            try:
                return int(value)
            except:
                return None
        return None

    @staticmethod
    def _get_float_value(value: str) -> Optional[float]:
        if value and value != "null":
            try:
                return float(value)
            except:
                return None
        return None

    @staticmethod
    def _get_uuid_value(value: str) -> Optional[UUID]:
        if value and value != "null":
            try:
                return UUID(value)
            except:
                return None
        return None

    @staticmethod
    def _get_datetime_value(value: str) -> Optional[datetime]:
        if value and value != "null":
            try:
                return datetime_from_iso_format_compat(value)
            except:
                return None
        return None

    @staticmethod
    def _get_timedelta_value(value: str) -> Optional[timedelta]:
        if value and value != "null":
            try:
                return parse_timedelta_string(value)
            except:
                return None
        return None

    @staticmethod
    def _get_date_value(value: str) -> Optional[date]:
        if value and value != "null":
            try:
                return date.fromisoformat(value)
            except:
                return None
        return None

    @staticmethod
    def _get_time_value(value: str) -> Optional[time]:
        if value and value != "null":
            try:
                return time_from_iso_format_compat(value)
            except:
                return None
        return None

    @staticmethod
    def _get_bytes_value(value: str) -> Optional[bytes]:
        if value and value != "null":
            try:
                return str(value).encode("utf-8")
            except:
                return None
        return None

    def _get_fields(self, raw_value: str) -> dict[str, str]:
        fields = raw_value.split('&')
        field_values = defaultdict(list)
        for field in fields:
            if '=' in field:
                key, value = field.split('=', 1)
                key = self._sanitize_key(key)
                value = value.strip()
                field_values[key].append(value)

        # Convert lists to comma-separated strings
        result: dict[str, str] = {}
        for key in field_values:
            result[key] = ','.join(field_values[key])
        return result

    def _sanitize_key(self, key: str) -> str:
        if not key:
            return key
        return unquote_plus(key.strip())
