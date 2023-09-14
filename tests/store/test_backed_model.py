# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All Rights Reserved.
# Licensed under the MIT License.
# See License in the project root for license information.
# ------------------------------------------------------------------------------

import pytest

def test_backed_model_return_only_changed_values_false(mock_user):
    # Getters retrieve all values from backing store
    assert mock_user.id == "84b3f7bf-6afb-46b2-9c6d-660c9b8c8ea0"
    assert mock_user.odata_type == "#microsoft.graph.mockEntity"
    assert mock_user.additional_data == {"extensionData": None}
    assert mock_user.business_phones == ["+1 732 555 0102"]

def test_backed_model_return_only_changed_values_true(mock_user):
    # Set the backing store to only return changed values
    mock_user.backing_store.return_only_changed_values = True
    # No changes have been made to the backing store
    # enumerate should return an empty list
    assert mock_user.backing_store.enumerate_() == []
    # change a property value
    mock_user.business_phones = ["+1 234 567 8901"]
    # returns the changed value
    assert mock_user.backing_store.enumerate_() == [('business_phones', (["+1 234 567 8901"], 1))]
    