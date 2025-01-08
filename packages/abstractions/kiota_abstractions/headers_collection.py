from __future__ import annotations

from typing import Union


class HeadersCollection():
    "Represents a collection of request/response headers"
    SINGLE_VALUE_HEADERS: set[str] = {"content-type", "content-encoding", "content-length"}

    def __init__(self) -> None:
        self._headers: dict[str, set[str]] = {}

    def try_get(self, key: str) -> Union[bool, set[str]]:
        """Gets the header values corresponding to a specific header name.

        Args:
            key (str): Header key.

        Returns:
            Union[bool, set[str]]: The header values for the specified header key or False.
        """
        if not key:
            raise ValueError("Header name cannot be null")
        key = key.lower()
        values = self._headers.get(key)
        if values:
            return values
        return False

    def get_all(self) -> dict[str, set[str]]:
        """Get all headers and values stored so far.

        Returns:
            dict[str, str]: The headers
        """
        return self._headers

    def get(self, header_name: str) -> set[str]:
        """Get header values corresponding to a specific header.
        
        Args:
            header_name (str): Header key.

        Returns:
            set[str]: Values for the header key
        """
        if not header_name:
            raise ValueError("Header name cannot be null")
        header_name = header_name.lower()
        values = self._headers.get(header_name)
        if not values:
            return set()
        return values

    def try_add(self, header_name: str, header_value: str) -> bool:
        """Adds values to the header with the specified name if it's not already present

        Args:
            header_name (str): The name of the header to add values to.
            header_value (str): The values to add to the header.

        Returns:
            bool: If the header value has been added to headers.
        """
        if not header_name:
            raise ValueError("Header name cannot be null")
        if header_value is None:
            raise ValueError("Header value cannot be null")
        header_name = header_name.lower()
        if header_name not in self._headers:
            self._headers[header_name] = {header_value}
            return True
        return False

    def add_all(self, headers: HeadersCollection) -> None:
        """Adds the specified headers to the collection.

        Args:
            headers (dict[str, str]): The headers to add.
        """
        if not headers:
            raise ValueError("Headers cannot be null")
        for key, values in headers.get_all().items():
            for value in values:
                self.add(key, value)

    def add(self, header_name: str, header_values: Union[str, list[str]]) -> None:
        """Adds values to the header with the specified name.

        Args:
            header_name (str): The name of the header to add values to.
            header_values (list[str]): The values to add to the header.
        """
        if not header_name:
            raise ValueError("Header name cannot be null")
        if header_values is None:
            raise ValueError("Header values cannot be null")
        if not header_values:  # empty list
            return
        header_name = header_name.lower()
        if isinstance(header_values, list):
            if header_name in self.SINGLE_VALUE_HEADERS:
                self._headers[header_name] = {header_values[0]}
            elif values := self.try_get(header_name):
                for header_value in header_values:
                    values.add(header_value)  #type: ignore
            else:
                self._headers[header_name] = set(header_values)
        else:
            if values := self.try_get(header_name):
                values.add(header_values)  #type: ignore
            else:
                self._headers[header_name] = {header_values}

    def keys(self) -> list[str]:
        """Gets the header names present in the collection.
        Returns:
            list[str]: The header names present in the collection.
        """
        return list(self._headers.keys())

    def count(self):
        """Gets the number of headers present in the collection."""
        return len(self._headers)

    def remove_value(self, header_name: str, header_value: str) -> Union[bool, set[str]]:
        """Removes the specified value from the header with the specified name.

        Args:
            header_name (str): The name of the header to remove the value from.
            header_value (str): The value to remove from the header.

        Returns:
            bool: _description_
        """
        if not header_name:
            raise ValueError("Header name cannot be null")
        if header_value is None:
            raise ValueError("Header value cannot be null")
        header_name = header_name.lower()
        values = self.try_get(header_name)
        if values:
            values.remove(header_value)  #type: ignore
            if bool(values):
                return values
            return self.remove(header_name)

        return False

    def remove(self, header_name: str) -> Union[bool, set[str]]:
        """Removes the header with the specified name.

        Args:
            header_name (str): The name of the header to remove.

        Returns:
            bool: True if the header has been removed, False otherwise.
        """
        if not header_name:
            raise ValueError("Header name cannot be null")
        header_name = header_name.lower()
        if self.contains(header_name):
            return self._headers.pop(header_name)
        return False

    def clear(self) -> None:
        """Removes all headers from the collection.
        """
        self._headers.clear()

    def contains(self, key: str) -> bool:
        """Checks whether the collection contains a specific header.

        Args:
            key (str): The name of the header to check for.

        Returns:
            bool: True if the header is present, false otherwise.
        """
        if not key:
            raise ValueError("Header name cannot be null")
        key = key.lower()
        return key in self._headers
