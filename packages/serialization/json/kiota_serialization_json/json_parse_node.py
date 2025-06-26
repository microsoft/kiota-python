from __future__ import annotations

import json
import re
import warnings
from collections.abc import Callable
from datetime import date, datetime, time, timedelta
from enum import Enum
from typing import Any, Optional, TypeVar
from uuid import UUID

from kiota_abstractions.date_utils import (
    parse_timedelta_string, datetime_from_iso_format_compat, time_from_iso_format_compat
)
from kiota_abstractions.serialization import Parsable, ParsableFactory, ParseNode

T = TypeVar("T", bool, str, int, float, UUID, datetime, timedelta, date, time, bytes)

U = TypeVar("U", bound=Parsable)

K = TypeVar("K", bound=Enum)


class JsonParseNode(ParseNode):

    def __init__(self, node: Any) -> None:
        """
        Args:
            node (Any): The JsonElement\
                to initialize the node with
        """
        self._json_node = node
        self._on_before_assign_field_values: Optional[Callable[[Parsable], None]] = None
        self._on_after_assign_field_values: Optional[Callable[[Parsable], None]] = None

    def get_child_node(self, identifier: str) -> Optional[ParseNode]:
        """Gets a new parse node for the given identifier
        Args:
            identifier (str): The identifier of the current node property
        Returns:
            Optional[ParseNode]: A new parse node for the given identifier
        """
        if not identifier:
            raise ValueError("identifier cannot be None or empty.")

        if isinstance(node := self._json_node, dict) and identifier in node:
            return self._create_new_node(node[identifier])
        return None

    def get_str_value(self) -> Optional[str]:
        """Gets the string value from the json node
        Returns:
            str: The string value of the node
        """
        return self._json_node if isinstance(self._json_node, str) else None

    def get_bool_value(self) -> Optional[bool]:
        """Gets the boolean value of the json node
        Returns:
            bool: The boolean value of the node
        """
        return self._json_node if isinstance(self._json_node, bool) else None

    def get_int_value(self) -> Optional[int]:
        """Gets the integer value of the json node
        Returns:
            int: The integer value of the node
        """
        return self._json_node if isinstance(self._json_node, int) else None

    def get_float_value(self) -> Optional[float]:
        """Gets the float value of the json node
        Returns:
            float: The number value of the node
        """
        return float(self._json_node) if isinstance(self._json_node, (float, int)) else None

    def get_uuid_value(self) -> Optional[UUID]:
        """Gets the UUID value of the json node
        Returns:
            UUID: The GUID value of the node
        """
        if isinstance(self._json_node, UUID):
            return self._json_node
        if isinstance(self._json_node, str):
            return UUID(self._json_node)
        return None

    def get_datetime_value(self) -> Optional[datetime]:
        """Gets the datetime value of the json node
        Returns:
            datetime: The datetime value of the node
        """
        if isinstance(self._json_node, datetime):
            return self._json_node

        if isinstance(self._json_node, str):
            if len(self._json_node) < 10:
                return None

            datetime_obj = datetime_from_iso_format_compat(self._json_node)
            if isinstance(datetime_obj, datetime):
                return datetime_obj
        return None

    def get_timedelta_value(self) -> Optional[timedelta]:
        """Gets the timedelta value of the node
        Returns:
            timedelta: The timedelta value of the node
        """
        if isinstance(self._json_node, timedelta):
            return self._json_node
        if isinstance(self._json_node, str):
            try:
                return parse_timedelta_string(self._json_node)
            except ValueError:
                return None
        return None

    def get_date_value(self) -> Optional[date]:
        """Gets the date value of the node
        Returns:
            date: The datevalue of the node in terms on year, month, and day.
        """
        if isinstance(self._json_node, date):
            return self._json_node
        if isinstance(self._json_node, str):
            datetime_obj = date.fromisoformat(self._json_node)
            if isinstance(datetime_obj, date):
                return datetime_obj
        return None

    def get_time_value(self) -> Optional[time]:
        """Gets the time value of the node
        Returns:
            time: The time value of the node in terms of hour, minute, and second.
        """
        if isinstance(self._json_node, time):
            return self._json_node
        if isinstance(self._json_node, str):
            datetime_obj = time_from_iso_format_compat(self._json_node)
            if isinstance(datetime_obj, time):
                return datetime_obj
        return None

    def get_collection_of_primitive_values(self, primitive_type: type[T]) -> Optional[list[T]]:
        """Gets the collection of primitive values of the node
        Args:
            primitive_type: The type of primitive to return.
        Returns:
            list[T]: The collection of primitive values
        """

        primitive_types = {bool, str, int, float, UUID, datetime, timedelta, date, time, bytes}

        def func(item):
            generic_type = primitive_type if primitive_type else type(item)
            current_parse_node = self._create_new_node(item)
            if generic_type in primitive_types:
                method = getattr(current_parse_node, f'get_{generic_type.__name__.lower()}_value')
                return method()
            raise Exception(f"Encountered an unknown type during deserialization {generic_type}")

        if isinstance(self._json_node, str):
            return list(map(func, json.loads(self._json_node)))
        return list(map(func, list(self._json_node)))

    def get_collection_of_object_values(self, factory: ParsableFactory[U]) -> Optional[list[U]]:
        """Gets the collection of type U values from the json node
        Returns:
            list[U]: The collection of model object values of the node
        """
        if isinstance(self._json_node, list):
            return list(
                map(
                    lambda x: self._create_new_node(x).get_object_value(factory),  # type: ignore
                    self._json_node,
                )
            )
        return []

    def get_collection_of_enum_values(self, enum_class: K) -> Optional[list[K]]:
        """Gets the collection of enum values of the json node
        Returns:
            list[K]: The collection of enum values
        """
        if isinstance(self._json_node, list):
            return list(
                map(
                    lambda x: self._create_new_node(x).get_enum_value(enum_class),  # type: ignore
                    self._json_node
                )
            )
        return []

    def get_enum_value(self, enum_class: K) -> Optional[K]:
        """Gets the enum value of the node
        Returns:
            Optional[K]: The enum value of the node
        """
        raw_key = str(self._json_node)
        if not raw_key:
            return None

        camel_case_key = None
        if raw_key.lower() == "none":
            # None is a reserved keyword in python
            camel_case_key = "None_"
        else:
            camel_case_key = raw_key[0].upper() + raw_key[1:]

        try:
            return enum_class[camel_case_key]  # type: ignore
        except KeyError:
            return None

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

    def get_bytes_value(self) -> Optional[bytes]:
        """Get a bytearray value from the nodes
        Returns:
            bytearray: The bytearray value from the nodes
        """
        # if the node is a string, we need to decode it
        # This ensures that the string is properly converted to bytes
        if isinstance(self._json_node, str):
            base64_string = self._json_node
        else:
            base64_string = json.dumps(self._json_node)
        if not base64_string:
            return None
        return base64_string.encode("utf-8")

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
        if not isinstance(self._json_node, dict):
            return

        item_additional_data = None
        if not hasattr(item, "additional_data") or item.additional_data is None:
            item_additional_data = {}
        else:
            item_additional_data = item.additional_data

        field_deserializers = item.get_field_deserializers()

        for field_name, field_value in self._json_node.items():
            if field_name in field_deserializers:
                if field_value is None:
                    continue
                field_deserializer = field_deserializers[field_name]
                field_deserializer(JsonParseNode(field_value))
            elif item_additional_data is not None:
                item_additional_data[field_name] = self.try_get_anything(field_value)
            else:
                warnings.warn(
                    f"Found additional property {field_name} to \
                    deserialize but the model doesn't support additional data"
                )

    def __is_four_digit_number(self, value: str) -> bool:
        pattern = r'^\d{4}$'
        return bool(re.match(pattern, value))

    def try_get_anything(self, value: Any) -> Any:
        if isinstance(value, (int, float, bool)) or value is None:
            return value
        if isinstance(value, list):
            return list(map(self.try_get_anything, value))
        if isinstance(value, dict):
            return dict(map(lambda x: (x[0], self.try_get_anything(x[1])), value.items()))
        if isinstance(value, str):
            try:
                if self.__is_four_digit_number(value):
                    return value
                if value.isdigit():
                    return value
                datetime_obj = datetime_from_iso_format_compat(value)
                return datetime_obj
            except ValueError:
                pass
            try:
                return UUID(value)
            except:
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

    def _create_new_node(self, node: Any) -> JsonParseNode:
        new_node: JsonParseNode = JsonParseNode(node)
        if self.on_before_assign_field_values:
            new_node.on_before_assign_field_values = self.on_before_assign_field_values
        if self.on_after_assign_field_values:
            new_node.on_after_assign_field_values = self.on_after_assign_field_values
        return new_node
