# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All Rights Reserved.
# Licensed under the MIT License.
# See License in the project root for license information.
# ------------------------------------------------------------------------------

from typing import Any, Callable, TypeVar, Generic, List, Tuple
import pytest

from kiota_abstractions.store import (
    BackingStoreFactorySingleton,
    InMemoryBackingStoreFactory,
)
from kiota_abstractions.store.backing_store import BackingStore
from kiota_abstractions.store.backing_store_factory import BackingStoreFactory
from kiota_abstractions.store.in_memory_backing_store import InMemoryBackingStore

T = TypeVar("T")


class MockTestBackingStore(BackingStore, Generic[T]):
    def __init__(self) -> None:
        self.store = {}
        self.subscriptions = {}
        self.init_complete = True
        self.return_only_changed_values = True

    def get(self, key: str) -> Any:
        return self.store.get(key, None)

    def set(self, key: str, value: Any) -> None:
        self.store.update({key: value})

    def clear(self) -> None:
        self.store.clear()

    def enumerate_(self) -> List[Tuple[str, Any]]:
        return list(self.store.values())

    def enumerate_keys_for_values_changed_to_null(self) -> List[str]:
        return list(k for k, v in self.store if v is None)

    def subscribe(
        self, callback: Callable[[str, Any, Any], None], subscription_id: str
    ) -> str:
        if subscription_id:
            self.subscriptions.update({subscription_id: callback})
        return subscription_id or ""

    def unsubscribe(self, subscription_id: str) -> None:
        self.subscriptions.pop(subscription_id)

    def get_is_initialization_completed(self) -> bool:
        return self.init_complete

    def set_is_initialization_completed(self, completed) -> None:
        self.init_complete = completed

    def get_return_only_changed_values(self) -> bool:
        return self.return_only_changed_values

    def set_return_only_changed_values(self, changed) -> None:
        self.return_only_changed_values = changed


class MockTestBackingStoreFactory(BackingStoreFactory):
    def create_backing_store(self) -> BackingStore:
        return MockTestBackingStore()


def test_backing_store_factory_default():
    bsf = BackingStoreFactorySingleton(backing_store_factory=None)
    assert isinstance(bsf.backing_store_factory, InMemoryBackingStoreFactory)


def test_backing_store_factory_is_singleton():
    """
    Test that the backing store factory that was initialized with the backing
    store singleton is not overridden when you initialize backing store factory
    singleton with a different backing store factory at runtime.
    """
    bsf = BackingStoreFactorySingleton(
        backing_store_factory=MockTestBackingStoreFactory()
    )
    bsf2 = BackingStoreFactorySingleton(
        backing_store_factory=InMemoryBackingStoreFactory()
    )
    assert bsf.get_instance() == bsf2.get_instance()
    assert bsf.backing_store_factory is bsf2.backing_store_factory
