# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All Rights Reserved.
# Licensed under the MIT License.
# See License in the project root for license information.
# ------------------------------------------------------------------------------

from collections.abc import Callable

from .parsable import Parsable
from .parse_node import ParseNode
from .parse_node_factory import ParseNodeFactory


class ParseNodeProxyFactory(ParseNodeFactory):
    """Proxy factory that allows the composition of before and after callbacks on existing factories
    """

    def __init__(
        self, concrete: ParseNodeFactory, on_before: Callable[[Parsable], None],
        on_after: Callable[[Parsable], None]
    ) -> None:
        """Creates a new proxy factory that wraps the specified concrete factory while composing
        the before and after callbacks.

        Args:
            concrete (ParseNodeFactory): The concrete factory to wrap.
            on_before (Callable[[Parsable], None]): The callback to invoke before the
            deserialization of any model object.
            on_after (Callable[[Parsable], None]): The callback to invoke after the deserialization
            of any model object.
        """
        if not concrete:
            raise ValueError("Concrete factory cannot be None")

        self._concrete = concrete
        self._on_before = on_before
        self._on_after = on_after

    def get_valid_content_type(self) -> str:
        """
        Returns:
            str: The valid content type for the ParseNodeFactory instance
        """
        return self._concrete.get_valid_content_type()

    def get_root_parse_node(self, content_type: str, content: bytes) -> ParseNode:
        """Create a parse node from the given stream and content type.

        Args:
            content_type (str): The content type of the parse node.
            content (bytes): The stream to read the parse node from.

        Returns:
            ParseNode: A parse node.
        """
        node = self._concrete.get_root_parse_node(content_type, content)
        original_before = node.on_before_assign_field_values
        original_after = node.on_after_assign_field_values

        def before_callback(value):
            if self._on_before:
                self._on_before(value)
            if callable(original_before):
                original_before(value)

        node.on_before_assign_field_values = before_callback

        def after_callback(value):
            if self._on_after:
                self._on_after(value)
            if callable(original_after):
                original_after(value)

        node.on_after_assign_field_values = after_callback

        return node
