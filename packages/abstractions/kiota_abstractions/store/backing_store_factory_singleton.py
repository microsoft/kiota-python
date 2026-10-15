# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All Rights Reserved.
# Licensed under the MIT License.
# See License in the project root for license information.
# ------------------------------------------------------------------------------

from typing import Optional

from kiota_abstractions.store.backing_store_factory import BackingStoreFactory
from kiota_abstractions.store.in_memory_backing_store_factory import InMemoryBackingStoreFactory


class BackingStoreFactorySingleton:
    """
    Ensures that there is only a single instance of a Backing Store Factory.
    """

    __instance: Optional["BackingStoreFactorySingleton"] = None
    _backing_store_factory: BackingStoreFactory

    def __new__(
        cls,
        backing_store_factory: Optional[BackingStoreFactory] = None
    ) -> "BackingStoreFactorySingleton":
        """
        Returns the single instance of the class, created on first use with an
        InMemoryBackingStoreFactory.
        """
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance._backing_store_factory = InMemoryBackingStoreFactory()
        return cls.__instance

    @classmethod
    def get_instance(cls) -> "BackingStoreFactorySingleton":
        """
        Returns the instance of the class.
        """
        return cls()

    def __init__(self, backing_store_factory: Optional[BackingStoreFactory] = None) -> None:
        """
        Replaces the backing store factory when one is given. None keeps the current one.
        """
        if backing_store_factory is not None:
            self._backing_store_factory = backing_store_factory

    @property
    def backing_store_factory(self) -> BackingStoreFactory:
        """Returns the set backing store"""
        return self._backing_store_factory

    @backing_store_factory.setter
    def backing_store_factory(self, backing_store_factory: BackingStoreFactory) -> None:
        """Sets the backing store to the value initialized in the singleton."""
        self._backing_store_factory = backing_store_factory
