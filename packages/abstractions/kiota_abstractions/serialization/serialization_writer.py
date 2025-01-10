from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from datetime import date, datetime, time, timedelta
from enum import Enum
from typing import Any, Optional, TypeVar
from uuid import UUID

from .parsable import Parsable

T = TypeVar("T")
U = TypeVar("U", bound=Parsable)
K = TypeVar("K", bound=Enum)


class SerializationWriter(ABC):
    """Defines an interface for serialization of objects to a stream
    """

    @abstractmethod
    def write_str_value(self, key: Optional[str], value: Optional[str]) -> None:
        """Writes the specified string value to the stream with an optional given key.

        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            value (Optional[str]): The string value to be written.
        """
        pass

    @abstractmethod
    def write_bool_value(self, key: Optional[str], value: Optional[bool]) -> None:
        """Writes the specified boolean value to the stream with an optional given key.

        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            value (Optional[bool]): The boolean value to be written.
        """
        pass

    @abstractmethod
    def write_int_value(self, key: Optional[str], value: Optional[int]) -> None:
        """Writes the specified integer value to the stream with an optional given key.

        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            value (Optional[int]): The integer value to be written.
        """
        pass

    @abstractmethod
    def write_float_value(self, key: Optional[str], value: Optional[float]) -> None:
        """Writes the specified float value to the stream with an optional given key.

        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            value (Optional[float]): The float value to be written.
        """
        pass

    @abstractmethod
    def write_uuid_value(self, key: Optional[str], value: Optional[UUID]) -> None:
        """Writes the specified uuid value to the stream with an optional given key.

        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            value (Optional[UUId]): The uuid value to be written.
        """
        pass

    @abstractmethod
    def write_datetime_value(self, key: Optional[str], value: Optional[datetime]) -> None:
        """Writes the specified datetime offset value to the stream with an optional given key.

        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            value (Optional[datetime]): The datetime offset value to be written.
        """
        pass

    @abstractmethod
    def write_timedelta_value(self, key: Optional[str], value: Optional[timedelta]) -> None:
        """Writes the specified timedelta value to the stream with an optional given key.

        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            value (Optional[timedelta]): The timedelta value to be written.
        """
        pass

    @abstractmethod
    def write_date_value(self, key: Optional[str], value: Optional[date]) -> None:
        """Writes the specified date value to the stream with an optional given key.

        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            value (Optional[date]): The date value to be written.
        """
        pass

    @abstractmethod
    def write_time_value(self, key: Optional[str], value: Optional[time]) -> None:
        """Writes the specified time value to the stream with an optional given key.

        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            value (Optional[time]): The time value to be written.
        """
        pass

    @abstractmethod
    def write_collection_of_primitive_values(
        self, key: Optional[str], values: Optional[list[T]]
    ) -> None:
        """Writes the specified collection of primitive values to the stream with an optional
        given key.

        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            values (Optional[list[T]]): The collection of primitive values to be written.
        """
        pass

    @abstractmethod
    def write_collection_of_object_values(
        self, key: Optional[str], values: Optional[list[U]]
    ) -> None:
        """Writes the specified collection of model objects to the stream with an optional
        given key.

        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            values (Optional[list[U]]): The collection of model objects to be written.
        """
        pass

    @abstractmethod
    def write_collection_of_enum_values(
        self, key: Optional[str], values: Optional[list[K]]
    ) -> None:
        """Writes the specified collection of enum values to the stream with an optional given key.

        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            values Optional[list[K]): The enum values to be written.
        """
        pass

    @abstractmethod
    def write_bytes_value(self, key: Optional[str], value: Optional[bytes]) -> None:
        """Writes the specified byte array as a base64 string to the stream with an optional
        given key.

        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            value (bytes): The bytes to be written.
        """
        pass

    @abstractmethod
    def write_object_value(
        self, key: Optional[str], value: Optional[U], *additional_values_to_merge: Optional[U]
    ) -> None:
        """Writes the specified model object to the stream with an optional given key.

        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            value (Parsable): The model object to be written.
            additional_values_to_merge (list[Parsable]): The additional values to merge to the
            main value when serializing an intersection wrapper.
        """
        pass

    @abstractmethod
    def write_enum_value(self, key: Optional[str], value: Optional[K]) -> None:
        """Writes the specified enum value to the stream with an optional given key.

        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
            value (Optional[K]): The enum value to be written.
        """
        pass

    @abstractmethod
    def write_null_value(self, key: Optional[str]) -> None:
        """Writes a null value for the specified key.

        Args:
            key (Optional[str]): The key to be used for the written value. May be null.
        """
        pass

    @abstractmethod
    def write_additional_data_value(self, value: dict[str, Any]) -> None:
        """Writes the specified additional data to the stream.
        Args:
            value (dict[str, Any]): he additional data to be written.
        """
        pass

    @abstractmethod
    def get_serialized_content(self) -> bytes:
        """Gets the value of the serialized content.

        Returns:
            bytes: The value of the serialized content.
        """
        pass

    @property
    @abstractmethod
    def on_before_object_serialization(self) -> Optional[Callable[[Parsable], None]]:
        """Gets the callback called before the object gets serialized.

        Returns:
            Optional[Callable[[Parsable], None]]:the callback called before the object
            gets serialized.
        """
        pass

    @on_before_object_serialization.setter
    @abstractmethod
    def on_before_object_serialization(self, value: Optional[Callable[[Parsable], None]]) -> None:
        """Sets the callback called before the objects gets serialized.

        Args:
            value (Optional[Callable[[Parsable], None]]): the callback called before the objects
            gets serialized.
        """
        pass

    @property
    @abstractmethod
    def on_after_object_serialization(self) -> Optional[Callable[[Parsable], None]]:
        """Gets the callback called after the object gets serialized.

        Returns:
            Optional[Optional[Callable[[Parsable], None]]]: the callback called after the object
            gets serialized.
        """
        pass

    @on_after_object_serialization.setter
    @abstractmethod
    def on_after_object_serialization(self, value: Optional[Callable[[Parsable], None]]) -> None:
        """Sets the callback called after the objects gets serialized.

        Args:
            value (Optional[Callable[[Parsable], None]]): the callback called after the objects
            gets serialized.
        """
        pass

    @property
    @abstractmethod
    def on_start_object_serialization(
        self
    ) -> Optional[Callable[[Parsable, SerializationWriter], None]]:
        """Gets the callback called right after the serialization process starts.

        Returns:
            Optional[Callable[[Parsable, SerializationWriter], None]]: the callback called
            right after the serialization process starts.
        """
        pass

    @on_start_object_serialization.setter
    @abstractmethod
    def on_start_object_serialization(
        self, value: Optional[Callable[[Parsable, SerializationWriter], None]]
    ) -> None:
        """Sets the callback called right after the serialization process starts.

        Args:
            value (Optional[Callable[[Parsable, SerializationWriter], None]]): the callback
            called right after the serialization process starts.
        """
        pass
