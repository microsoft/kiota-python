# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All Rights Reserved.
# Licensed under the MIT License.
# See License in the project root for license information.
# ------------------------------------------------------------------------------

from ..serialization import SerializationWriterFactory, SerializationWriterProxyFactory
from .backed_model import BackedModel


class BackingStoreSerializationWriterProxyFactory(SerializationWriterProxyFactory):
    """Proxy implementation of SerializationWriterFactory for the backing store that
    automatically sets the state of the backing store when serializing.
    """

    def __init__(self, concrete: SerializationWriterFactory) -> None:
        """Initializes a new instance of the BackingStoreSerializationWriterProxyFactory class
        given a concrete implementation of SerializationWriterFactory.

        Args:
            concrete (SerializationWriterFactory):  a concrete implementation of
            SerializationWriterFactory to wrap.
        """

        def on_before(x):
            if isinstance(x, BackedModel):
                backed_model = x
                backing_store = backed_model.backing_store
                if backing_store:
                    backing_store.return_only_changed_values = True

        def on_after(x):
            if isinstance(x, BackedModel):
                backed_model = x
                backing_store = backed_model.backing_store
                if backing_store:
                    backing_store.return_only_changed_values = False
                    backing_store.is_initialization_completed = True

        def on_start(x, y):
            if isinstance(x, BackedModel):
                backed_model = x
                backing_store = backed_model.backing_store
                if backing_store:
                    keys = backing_store.enumerate_keys_for_values_changed_to_null()
                    for key in keys:
                        y.write_null_value(key)

        super().__init__(concrete, on_before, on_after, on_start)
