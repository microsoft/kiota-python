from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class AdditionalDataHolder:
    """Defines a contract for models that can hold additional data besides the described properties.
    """
    # Stores the additional data for this object that did not belong to the properties.
    additional_data: Dict[str, Any] = field(default_factory=dict)
