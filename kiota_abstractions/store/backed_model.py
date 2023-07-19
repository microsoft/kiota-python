# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All Rights Reserved.
# Licensed under the MIT License.
# See License in the project root for license information.
# ------------------------------------------------------------------------------

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from .backing_store import BackingStore


@dataclass
class BackedModel:
    """Defines the contracts for a model that is backed by a store.
    """
    # Stores model information.
    backing_store: BackingStore

    def __setattr__(self, prop, val):
        if not prop == "backing_store":
            self.__backing_store.set(prop, val)
            super().__setattr__(prop, self.__backing_store.get(prop))
        super().__setattr__(prop, val)

    @property
    def __backing_store(self):
        return self.backing_store

    @__backing_store.setter
    def __backing_store(self, value):
        self.backing_store = value
