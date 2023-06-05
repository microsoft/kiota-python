from typing import Callable, Dict, List

from . import Parsable, ParseNode


class ParseNodeHelper:

    @staticmethod
    def merge_deserializers_for_intersection_wrapper(
        targets: List[Parsable]
    ) -> Dict[str, Callable[[ParseNode], None]]:
        """Merges a collection of parsable field deserializers into a single collection.

        Args:
            targets (List[Parsable]):

        Returns:
            Dict[str, Callable[[ParseNode], None]]:
        """
        if not targets:
            raise ValueError(
                f"Invalid value {targets} for targets. At least one target must be provided."
            )

        result = {}
        for target in targets:
            target_field_deserializers = target.get_field_deserializers()
            for key, val in target_field_deserializers.items():
                if key not in result:
                    result[key] = val

        return result
