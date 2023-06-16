from typing import Callable, Dict, List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from . import Parsable, ParseNode


class ParseNodeHelper:

    @staticmethod
    def merge_deserializers_for_intersection_wrapper(
        *targets: Parsable
    ) -> Dict[str, Callable[[ParseNode], None]]:
        """Merges a collection of parsable field deserializers into a single collection.

        Args:
            targets (tuple[Parsable, ...]):

        Returns:
            Dict[str, Callable[[ParseNode], None]]:
        """
        if targets is None:
            raise ValueError("targets cannot be None")
        if not targets:
            raise ValueError("At least one target must be provided.")

        merged_deserializers = {}
        for target in targets:
            if target is not None:
                for key, val in target.get_field_deserializers().items():
                    if key not in merged_deserializers:
                        merged_deserializers[key] = val

        return merged_deserializers
