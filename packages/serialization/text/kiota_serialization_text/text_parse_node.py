from __future__ import annotations

import base64
from collections.abc import Callable
from datetime import date, datetime, time, timedelta
from enum import Enum
from typing import Optional, TypeVar
from uuid import UUID

from kiota_abstractions.date_utils import (
    parse_timedelta_string, datetime_from_iso_format_compat, time_from_iso_format_compat
)
from kiota_abstractions.serialization import Parsable, ParsableFactory, ParseNode

T = TypeVar("T", bool, str, int, float, UUID, datetime, timedelta, date, time, bytes)

U = TypeVar("U", bound=Parsable)

K = TypeVar("K", bound=Enum)


class TextParseNode(ParseNode):
    """The ParseNode implementation for the text/plain content type
    """

    NO_STRUCTURED_DATA_MESSAGE = 'Text does not support structured data'

    on_before_assign_field_values: Optional[Callable[[Parsable], None]] = None
    on_after_assign_field_values: Optional[Callable[[Parsable], None]] = None

    def __init__(self, text: str) -> None:
        """ Initializes a new instance of the TextParseNode class
        Args:
            text (str):The text value to initialize the node with
        """
        if text or text is False:
            self._text = text

    def get_str_value(self) -> Optional[str]:
        """Gets the string value from the text node
        Returns:
            str: The string value of the node
        """
        if self._text:
            return str(self._text)
        return None

    def get_child_node(self, identifier: str) -> Optional[ParseNode]:
        """Gets a new parse node for the given identifier
        Args:
            identifier (str): The identifier of the current node property
        Returns:
            Optional[ParseNode]: A new parse node for the given identifier
        """
        raise Exception(self.NO_STRUCTURED_DATA_MESSAGE)

    def get_bool_value(self) -> Optional[bool]:
        """Gets the boolean value of the text node
        Returns:
            bool: The boolean value of the node
        """
        if self._text or (self._text is False):
            return bool(self._text)
        return None

    def get_int_value(self) -> Optional[int]:
        """Gets the integer value of the text node
        Returns:
            int: The integer value of the node
        """
        if self._text:
            return int(self._text)
        return None

    def get_float_value(self) -> Optional[float]:
        """Gets the floating point value of the text node
        Returns:
            float: The floating point value of the node
        """
        if self._text:
            return float(self._text)
        return None

    def get_uuid_value(self) -> Optional[UUID]:
        """Gets the UUID value of the text node
        Returns:
            UUID: The UUID value of the node
        """
        if self._text:
            return UUID(self._text)
        return None

    def get_datetime_value(self) -> Optional[datetime]:
        """Gets the datetime value of the text node
        Returns:
            datetime: The datetime value of the node
        """
        datetime_str = self.get_str_value()
        if datetime_str:
            return datetime_from_iso_format_compat(datetime_str)
        return None

    def get_timedelta_value(self) -> Optional[timedelta]:
        """Gets the timedelta value of the node
        Returns:
            timedelta: The timedelta value of the node
        """
        datetime_str = self.get_str_value()
        if datetime_str:
            return parse_timedelta_string(datetime_str)
        return None

    def get_date_value(self) -> Optional[date]:
        """Gets the date value of the node
        Returns:
            date: The datevalue of the node in terms on year, month, and day.
        """
        datetime_str = self.get_str_value()
        if datetime_str:
            return date.fromisoformat(datetime_str)
        return None

    def get_time_value(self) -> Optional[time]:
        """Gets the time value of the node
        Returns:
            time: The time value of the node in terms of hour, minute, and second.
        """
        datetime_str = self.get_str_value()
        if datetime_str:
            return time_from_iso_format_compat(datetime_str)
        return None

    def get_collection_of_primitive_values(self, primitive_type: type[T]) -> list[T]:
        """Gets the collection of primitive values of the node
        Args:
            primitive_type: The type of primitive to return.
        Returns:
            list[T]: The collection of primitive values
        """
        raise Exception(self.NO_STRUCTURED_DATA_MESSAGE)

    def get_collection_of_object_values(self, factory: ParsableFactory[U]) -> list[U]:
        """Gets the collection of type U values from the text node
        Returns:
            list[U]: The collection of model object values of the node
        """
        raise Exception(self.NO_STRUCTURED_DATA_MESSAGE)

    def get_collection_of_enum_values(self, enum_class: K) -> Optional[list[K]]:
        """Gets the collection of enum values of the text node
        Returns:
            list[K]: The collection of enum values
        """
        raise Exception(self.NO_STRUCTURED_DATA_MESSAGE)

    def get_enum_value(self, enum_class: K) -> Optional[K]:
        """Gets the enum value of the node
        Returns:
            Optional[K]: The enum value of the node
        """
        raw_key = self.get_str_value()
        camel_case_key = None
        if raw_key:
            camel_case_key = raw_key[0].upper() + raw_key[1:]
        if camel_case_key:
            try:
                return enum_class[camel_case_key]  # type: ignore
            except KeyError:
                raise Exception(f'Invalid key: {camel_case_key} for enum {enum_class}.')
        return None

    def get_object_value(self, factory: ParsableFactory[U]) -> U:
        """Gets the model object value of the node
        Returns:
            Parsable: The model object value of the node
        """
        raise Exception(self.NO_STRUCTURED_DATA_MESSAGE)

    def get_bytes_value(self) -> Optional[bytes]:
        """Get a bytes value from the node
        Returns:
            bytes: The bytes value from the node
        """
        base64_string = self.get_str_value()
        if not base64_string:
            return None
        base64_bytes = base64_string.encode("utf-8")
        return base64.b64decode(base64_bytes)

    def get_on_before_assign_field_values(self) -> Optional[Callable[[Parsable], None]]:
        """Gets the callback called before the node is deserialized.
        Returns:
            Callable[[Parsable], None]: the callback called before the node is deserialized.
        """
        return self.on_before_assign_field_values

    def get_on_after_assign_field_values(self) -> Optional[Callable[[Parsable], None]]:
        """Gets the callback called before the node is deserialized.
        Returns:
            Callable[[Parsable], None]: the callback called before the node is deserialized.
        """
        return self.on_after_assign_field_values

    def set_on_before_assign_field_values(self, value: Callable[[Parsable], None]) -> None:
        """Sets the callback called before the node is deserialized.
        Args:
            value (Callable[[Parsable], None]): the callback called before the node is
            deserialized.
        """
        self.on_before_assign_field_values = value

    def set_on_after_assign_field_values(self, value: Callable[[Parsable], None]) -> None:
        """Sets the callback called after the node is deserialized.
        Args:
            value (Callable[[Parsable], None]): the callback called after the node is
            deserialized.
        """
        self.on_after_assign_field_values = value
