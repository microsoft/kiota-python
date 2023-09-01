# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All Rights Reserved.
# Licensed under the MIT License.
# See License in the project root for license information.
# ------------------------------------------------------------------------------

from kiota_abstractions.store.backing_store_factory import BackingStoreFactory
from kiota_abstractions.store.in_memory_backing_store_factory import InMemoryBackingStoreFactory


class BackingStoreFactorySingleton:
    """
    Ensures that there is only a single instance of a Backing Store Factory.
    """

    def __new__(cls, *args, **kwargs):
        """
        Creates a single instance of the class during instantiation. It also
        ensures that the backing store factory that was set in the first
        instantion of the class will be the default during run time.
        """
        try:
            bs_arg = args[0]
        except IndexError:
            bs_arg = kwargs.get("backing_store_factory", None)

        bs_property = hasattr(cls, "backing_store_factory")
        if not hasattr(cls, "__instance"):
            if bs_property and isinstance(bs_arg, BackingStoreFactory):
                cls.backing_store_factory = bs_arg
            else:
                # Default backing store is InMemoryBackingStoreFactory
                cls.backing_store_factory = InMemoryBackingStoreFactory()
            cls.__instance = super(BackingStoreFactorySingleton, cls).__new__(cls)
        return cls.__instance

    @classmethod
    def get_instance(cls):
        """
        Returns the instance of the class.
        """
        return cls.__instance

    def __init__(self, backing_store_factory: BackingStoreFactory) -> None:
        self._backing_store_factory = backing_store_factory

    @property
    def backing_store_factory(self) -> BackingStoreFactory:
        """Returns the set backing store"""
        return self._backing_store_factory

    @backing_store_factory.setter
    def backing_store_factory(self, backing_store_factory: BackingStoreFactory):
        """Sets the backing store to the value initialized in the singleton."""
        self._backing_store_factory = backing_store_factory
