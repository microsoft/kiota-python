# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All Rights Reserved.
# Licensed under the MIT License.
# See License in the project root for license information.
# ------------------------------------------------------------------------------

from .backing_store import BackingStore
from .backing_store_factory import BackingStoreFactory
from .in_memory_backing_store import InMemoryBackingStore


class InMemoryBackingStoreFactory(BackingStoreFactory):
    """This class is used to create instances of InMemoryBackingStore
    """

    def create_backing_store(self) -> BackingStore:
        return InMemoryBackingStore()
