import json
from enum import Enum

import pytest

from kiota_serialization_json.json_parse_node import JsonParseNode


class RiskLevel(Enum):
    None_ = 'none'
    Low = 'low'


@pytest.mark.parametrize(
    'payload, expected', [
        ('null', None),
        ('"none"', RiskLevel.None_),
        ('"low"', RiskLevel.Low),
    ]
)
def test_nullable_enum_distinguishes_null_from_none_member(payload, expected):
    node = JsonParseNode(json.loads(payload))
    assert node.get_enum_value(RiskLevel) is expected


def test_nullable_enum_collection_preserves_null_entries():
    node = JsonParseNode(json.loads('["none", null, "low"]'))
    assert node.get_collection_of_enum_values(RiskLevel) == [RiskLevel.None_, None, RiskLevel.Low]
