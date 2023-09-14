# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All Rights Reserved.
# Licensed under the MIT License.
# See License in the project root for license information.
# ------------------------------------------------------------------------------

from dataclasses import dataclass, fields

from .backing_store import BackingStore


@dataclass
class BackedModel:
    """Defines the contracts for a model that is backed by a store.
    """
    # Stores model information.
    backing_store: BackingStore

    def __post_init__(self):
        self.backing_store.is_initialization_completed = True
        for field in fields(self):
            if field.name != "backing_store":
                field_val = getattr(self, field.name)
                if field_val is not field.default:
                    self.backing_store.set(field.name, field_val)

    def __setattr__(self, prop, val):
        if prop == "backing_store":
            super().__setattr__(prop, val)
        else:
            self.backing_store.set(prop, val)
            super().__setattr__(prop, self.backing_store.get(prop))
