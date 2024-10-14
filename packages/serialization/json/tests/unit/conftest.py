import json

import pytest

url: str = "https://graph.microsoft.com/v1.0/$metadata#users/$entity"


@pytest.fixture
def user1_json():
    return '{"id": "8f841f30-e6e3-439a-a812-ebd369559c36", '\
            '"office_location": "dunhill", '\
            '"updated_at": "2021-07-29T03:07:25Z", '\
            '"birthday": "2000-09-04", '\
            '"business_phones": ["+1 205 555 0108"], '\
            '"mobile_phone": null, '\
            '"is_active": true, '\
            '"additional_data": {"@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users/$entity", '\
            '"manager": {"id": "8f841f30-e6e3-439a-a812-ebd369559c36", '\
                '"updated_at": "2022-01-27T12:59:45.596117+00:00", "is_active": true}, '\
            '"approvers": [{"id": "8f841f30-e6e3-439a-a812-ebd369559c36", '\
                '"updated_at": "2022-01-27T12:59:45.596117+00:00", "is_active": true}, '\
                '{"display_name": "John Doe", "age": 32}], '\
            '"data": {'\
                '"groups": ['\
                    '{"friends": [{"display_name": "John Doe", "age": 32}]}'\
                ']'\
            '}}}'\


@pytest.fixture
def user2_json():

    return '{"id": 2, "display_name": "MOD Administrator", "age": 32, "gpa": 3.9}'


@pytest.fixture
def users_json():
    return '[{"id": "8f841f30-e6e3-439a-a812-ebd369559c36", '\
            '"office_location": "dunhill", '\
            '"updated_at": "2021-07-29T03:07:25Z", '\
            '"birthday": "2000-09-04", '\
            '"business_phones": ["+1 205 555 0108"], '\
            '"mobile_phone": null, '\
            '"is_active": true}, '\
            '{"id": "8f841f30-e6e3-439a-a812-ebd369559c36", '\
            '"office_location": "dunhill", '\
            '"updated_at": "2021-07-29T03:07:25Z", '\
            '"birthday": "2000-09-04", '\
            '"business_phones": ["+1 205 555 0108"], '\
            '"mobile_phone": null, '\
            '"is_active": true}]'


@pytest.fixture
def sample_entity_json():

    entity_json = json.dumps(
        {
            "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#$entity",
            "id": "8f841f30-e6e3-439a-a812-ebd369559c36"
        }
    )
    return entity_json
