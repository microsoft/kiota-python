# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All Rights Reserved.
# Licensed under the MIT License.
# See License in the project root for license information.
# ------------------------------------------------------------------------------

from collections.abc import Callable
from typing import Any, Generic, NamedTuple, Optional
from uuid import uuid4

from typing_extensions import TypeVar

from .backed_model import BackedModel
from .backing_store import BackingStore

T = TypeVar("T", default=object)


class _Collection(NamedTuple):
    """A stored list and its size when it was set, so a size change marks it dirty."""
    items: list[Any]
    size: int


class InMemoryBackingStore(BackingStore[T], Generic[T]):
    """In-memory implementation of the backing store. Allows for dirty tracking of changes."""

    def __init__(self) -> None:

        self.__id = str(uuid4())
        self.__subscriptions: dict[str, Callable[[str, Any, Any], None]] = {}
        self.__store: dict[str, tuple[bool, T, Optional[_Collection]]] = {}
        self.__initialization_completed: bool = False
        self.__return_only_changed_values: bool = False

    @property
    def is_initialization_completed(self) -> bool:
        """Flag to show the initialization status of the store."""
        return self.__initialization_completed

    @is_initialization_completed.setter
    def is_initialization_completed(self, value: bool) -> None:
        self.__initialization_completed = value
        for key in list(self.__store):
            _, val, collection = self.__store[key]
            if isinstance(val, BackedModel):
                # forward the initialization status to nested BackedModel instances
                val.backing_store.is_initialization_completed = value
            self._ensure_collection_size_is_consistent(key, val, collection)
            _, val, collection = self.__store[key]
            self.__store[key] = (not value, val, collection)

    @property
    def return_only_changed_values(self) -> bool:
        """Determines whether the backing store should only return changed values when queried."""
        return self.__return_only_changed_values

    @return_only_changed_values.setter
    def return_only_changed_values(self, value: bool) -> None:
        """Sets the flag to determines whether the backing store should only return changed values
        when queried."""
        self.__return_only_changed_values = value

    def get(self, key: str) -> Optional[T]:
        """Gets the specified object with the given key from the store.

        Args:
            key (str): The key to search with

        Returns:
            Optional[T]: An instance of T
        """
        if not key:
            raise ValueError("Key cannot be empty or None")

        result = self.__store.get(key)
        if result:
            _, result_value, collection = result
            self._ensure_collection_size_is_consistent(key, result_value, collection)
            if self.return_only_changed_values is False or (
                self.return_only_changed_values is True and self.__store[key][0]
            ):
                return result_value
            return None
        return None

    def set(self, key: str, value: T) -> None:
        """Sets the specified object with the given key in the store.

        Args:
            key (str): The key to use
            value (T): The object value to store
        """
        if not key:
            raise ValueError("Key cannot be empty or None")

        old_value = self.__store.get(key)
        collection = _Collection(value, len(value)) if isinstance(value, list) else None
        value_to_add = (self.is_initialization_completed, value, collection)

        if key not in self.__store:
            if isinstance(value, BackedModel) and value.backing_store:
                # if its the first time adding a BackedModel property to the store, subscribe
                # to its BackingStore and use the events to flag the property is "dirty"
                value.backing_store.is_initialization_completed = True
                value.backing_store.subscribe(
                    lambda prop_key, old_val, new_val: self.set(key, value)
                )
        if isinstance(value, list):
            # if its a collection, subscribe to the collection's item BackingStores and use
            # the events to flag the collection property is "dirty"
            for item in value:
                if isinstance(item, BackedModel) and item.backing_store:
                    item.backing_store.is_initialization_completed = True
                    item.backing_store.subscribe(
                        lambda prop_key, old_val, new_val: self.set(key, value),
                        f"{self.__id}:{key}"
                    )

        self.__store[key] = value_to_add
        for sub in list(self.__subscriptions):
            self.__subscriptions[sub](key, None if old_value is None else old_value[1], value)
            # sub(key, old_value, value_to_add)

    def enumerate_(self) -> list[tuple[str, Any]]:
        """Enumerate the values in the store based on the ReturnOnlyChangedValues configuration
        value

        Returns:
            list[tuple[str, Any]]: A collection of changed values or the whole store based on the
            ReturnOnlyChangedValues configuration value.
        """

        # refresh the state of collection properties if they've changed in size.
        if self.return_only_changed_values:
            for key, (_, val, collection) in self.__store.items():
                self._ensure_collection_size_is_consistent(key, val, collection)

        return [
            (key, val if collection is None else collection)
            for key, (changed, val, collection) in list(self.__store.items())
            if changed or not self.return_only_changed_values
        ]

    def enumerate_keys_for_values_changed_to_null(self) -> list[str]:
        """Enumerate the values in the store that have changed to None

        Returns:
            list[str]: A collection of strings containing keys changed to None
        """
        return [key for key, val in self.__store.items() if val[0] and val[1] is None]

    def subscribe(
        self,
        callback: Callable[[str, Any, Any], None],
        subscription_id: Optional[str] = None
    ) -> str:
        """Adds a callback to subscribe to events in the store with the given subscription id

        Args:
            callback (Callable[[str, Any, Any], None]): The callback to add
            subscription_id (Optional[str]): The subscription id to use for subscription

        Returns:
            str: The id of the subscription
        """
        if not callable(callback):
            raise ValueError("Callback must be a callable function")

        if not subscription_id:
            subscription_id = str(uuid4())

        self.__subscriptions[subscription_id] = callback
        return subscription_id

    def unsubscribe(self, subscription_id: str) -> None:
        """De-register the callback with the given subscriptionId

        Args:
            subscription_id (str): The id of the subscription to de-register
        """
        del self.__subscriptions[subscription_id]

    def clear(self) -> None:
        """Clears the store"""
        self.__store.clear()

    def _ensure_collection_size_is_consistent(
        self, key: str, entry: T, collection: Optional[_Collection]
    ) -> None:
        """Checks if entry of type collection has changed in size.
        If so, dirty tracks the change by calling set()

        Args:
            key (str): _description_
            entry (T): the stored value
            collection (Optional[_Collection]): the stored list and its size, if entry is a list
        """
        if collection is not None:
            backed_models = [item for item in collection.items if isinstance(item, BackedModel)]
            for backed_model in backed_models:
                values = backed_model.backing_store.enumerate_()
                for value in values:
                    # Call get() on nested properties so that this method may be called recursively
                    # to ensure collections are consistent
                    backed_model.backing_store.get(value[0])

            if len(collection.items) != collection.size:
                self.set(key, entry)  # dirty track the change

        elif isinstance(entry, BackedModel):
            values = entry.backing_store.enumerate_()
            for value in values:
                # Call get() on nested properties so that this method may be called recursively
                # to ensure collections are consistent
                entry.backing_store.get(value[0])
