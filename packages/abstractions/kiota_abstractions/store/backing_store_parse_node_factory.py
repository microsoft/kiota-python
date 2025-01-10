# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All Rights Reserved.
# Licensed under the MIT License.
# See License in the project root for license information.
# ------------------------------------------------------------------------------

from ..serialization import ParseNodeFactory, ParseNodeProxyFactory
from .backed_model import BackedModel


class BackingStoreParseNodeFactory(ParseNodeProxyFactory):
    """Proxy implementation of ParseNodeFactory for the backing store that automatically sets the
    state of the backing store when deserializing.
    """

    def __init__(self, concrete: ParseNodeFactory) -> None:
        """ Initializes a new instance of the BackingStoreParseNodeFactory class given a concrete
        implementation ParseNodeFactory.
        """

        def on_before_deserialization(x):
            if isinstance(x, BackedModel) and x.backing_store:
                x.backing_store.is_initialization_completed = False

        def on_after_deserialization(x):
            if isinstance(x, BackedModel) and x.backing_store:
                x.backing_store.is_initialization_completed = True

        super().__init__(concrete, on_before_deserialization, on_after_deserialization)
