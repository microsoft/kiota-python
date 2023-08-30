# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All Rights Reserved.
# Licensed under the MIT License.
# See License in the project root for license information.
# ------------------------------------------------------------------------------

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, List, Any, Tuple, Dict, Optional
import pytest

from kiota_abstractions.authentication.access_token_provider import AccessTokenProvider
from kiota_abstractions.authentication.allowed_hosts_validator import (
    AllowedHostsValidator,
)
from kiota_abstractions.request_information import RequestInformation
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from kiota_abstractions.store import BackedModel, BackingStore, BackingStoreFactorySingleton


class MockAccessTokenProvider(AccessTokenProvider):
    def __init__(self):
        self.token = None

    async def get_authorization_token(
        self,
        url: str,
        additional_authentication_context: Dict[str, Any] = {}
    ) -> str:
        return "SomeToken"

    def get_allowed_hosts_validator(self) -> AllowedHostsValidator:
        return AllowedHostsValidator(["example.com"])

@dataclass
class MockEntity(Parsable, AdditionalDataHolder, BackedModel):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: Dict[str, Any] = field(default_factory=dict)
    # Stores model information.
    backing_store : BackingStore = field(default_factory=BackingStoreFactorySingleton(backing_store_factory=None).backing_store_factory.create_backing_store)
    # The id property
    id: Optional[str] = None
    # The OdataType property
    odata_type: str = "#microsoft.graph.mockEntity"
    # The telephone numbers for the user. NOTE: Although this is a string collection, only one number can be set for this property. Read-only for users synced from on-premises directory. Returned by default. Supports $filter (eq, not, ge, le, startsWith).
    business_phones: Optional[List[str]] = None
    # The user or contact that is this user&apos;s manager. Read-only. (HTTP Methods: GET, PUT, DELETE.). Supports $expand.
    manager: Optional[MockEntity] = None
    # The user or contact that is this user& works with.
    colleagues: Optional[List[MockEntity]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: Optional[ParseNode] = None):
        """
        Creates a new instance of the appropriate class based on discriminator value
        Args:
            parse_node: The parse node to use to read the discriminator value and create the object
        Returns: AccessAction
        """
        if not parse_node:
            raise TypeError("parse_node cannot be null.")
        return MockEntity()
    
    def get_field_deserializers(self,) -> Dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: Dict[str, Callable[[ParseNode], None]]
        """
        fields: Dict[str, Callable[[Any], None]] = {
            "@odata.type": lambda n : setattr(self, 'odata_type', n.get_str_value()),
            "id": lambda n : setattr(self, 'id', n.get_str_value()),
            "businessPhones": lambda n : setattr(self, 'business_phones', n.get_collection_of_primitive_values(str)),
            "manager": lambda n : setattr(self, 'manager', n.get_object_value(MockEntity)),
            "colleagues": lambda n : setattr(self, 'colleagues', n.get_collection_of_object_values(MockEntity)),
        }
        return fields
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        Args:
            writer: Serialization writer to use to serialize this model
        """
        if not writer:
            raise TypeError("writer cannot be null.")
        writer.write_str_value("@odata.type", self.odata_type)
        writer.write_additional_data_value(self.additional_data)
        writer.write_str_value("id", self.id)
        writer.write_collection_of_primitive_values("businessPhones", self.business_phones)
        writer.write_object_value("manager", self.manager)
        writer.write_collection_of_object_values("colleagues", self.colleagues)
    
@pytest.fixture
def mock_user():
    user = MockEntity()
    user.id = "84b3f7bf-6afb-46b2-9c6d-660c9b8c8ea0"
    user.additional_data = {"extensionData": None}
    user.business_phones = ["+1 732 555 0102"]
    user.backing_store.is_initialization_completed = True
    return user

@pytest.fixture
def mock_request_information():
    request_info = RequestInformation()
    request_info.url = "https://example.com"
    return request_info


@pytest.fixture
def mock_access_token_provider():
    return MockAccessTokenProvider()
