from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from . import Parsable, ParseNode


class ParseNodeHelper:

    @staticmethod
    def merge_deserializers_for_intersection_wrapper(
        *targets: Optional[Parsable]
    ) -> dict[str, Callable[[ParseNode], None]]:
        """Merges a collection of parsable field deserializers into a single collection.

        Args:
            targets (tuple[Parsable, ...]):

        Returns:
            dict[str, Callable[[ParseNode], None]]:
        """
        if not targets:
            raise TypeError("targets cannot be null.")

        merged_deserializers = {}
        for target in targets:
            if target is not None:
                for key, val in target.get_field_deserializers().items():
                    if key not in merged_deserializers:
                        merged_deserializers[key] = val

        return merged_deserializers
