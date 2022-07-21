from unittest.mock import patch

import pytest
from persephone_client import Persephone

from src.domain.exceptions.model import InternalServerError
from src.domain.models.request.model import CompanyDirector
from src.repositories.step_validator.repository import StepValidator
from src.repositories.user.repository import UserRepository
from src.services.employ_data.service import CompanyDataService

tax_residence_model_dummy = CompanyDirector(
    **{
    "is_company_director": True,
    "company_name": "Lalau",
    "company_ticker": "LALA4"
}
)

payload_dummy = {
    "x_thebes_answer": "x_thebes_answer",
    "data": {"user": {"unique_id": "unique_id"}},
}


def test___model_company_director_data_to_persephone():
    company_director = True
    user_is_company_director_of = "string"
    company_ticker_that_user_is_director_of = "string"
    unique_id = "string"
    result = CompanyDataService._CompanyDataService__model_company_director_data_to_persephone(
        company_director,
        user_is_company_director_of,
        company_ticker_that_user_is_director_of,
        unique_id,
    )
    expected_result = {
            "unique_id": unique_id,
            "company_director": company_director,
            "user_is_company_director_of": user_is_company_director_of,
            "company_ticker_that_user_is_director_of": company_ticker_that_user_is_director_of,
        }
    assert result == expected_result


@pytest.mark.asyncio
@patch.object(UserRepository, "update_user")
@patch.object(Persephone, "send_to_persephone")
@patch.object(StepValidator, "validate_onboarding_step")
async def test_update_company_director_data_for_us(
    step_validator_mock, persephone_client_mock, update_user_mock
):
    persephone_client_mock.return_value = (True, 0)
    update_user_mock.return_value = True
    result = await CompanyDataService.update_company_director_data_for_us(
        tax_residence_model_dummy, payload_dummy
    )
    expected_result = None

    assert result == expected_result
    assert step_validator_mock.called
    assert persephone_client_mock.called
    assert update_user_mock.called


@pytest.mark.asyncio
@patch.object(UserRepository, "update_user")
@patch.object(Persephone, "send_to_persephone")
@patch.object(StepValidator, "validate_onboarding_step")
async def test_update_company_director_data_for_us_when_cant_send_to_persephone(
    step_validator_mock, persephone_client_mock, update_user_mock
):
    persephone_client_mock.return_value = (False, 0)
    update_user_mock.return_value = True
    with pytest.raises(InternalServerError):
        result = await CompanyDataService.update_company_director_data_for_us(
            tax_residence_model_dummy, payload_dummy
        )

    assert step_validator_mock.called
    assert persephone_client_mock.called
    assert not update_user_mock.called


@pytest.mark.asyncio
@patch.object(UserRepository, "update_user")
@patch.object(Persephone, "send_to_persephone")
@patch.object(StepValidator, "validate_onboarding_step")
async def test_update_company_director_data_for_us_when_cant_update_user_register(
    step_validator_mock, persephone_client_mock, update_user_mock
):
    persephone_client_mock.return_value = (True, 0)
    update_user_mock.return_value = False
    with pytest.raises(InternalServerError):
        result = await CompanyDataService.update_company_director_data_for_us(
            tax_residence_model_dummy, payload_dummy
        )

    assert step_validator_mock.called
    assert persephone_client_mock.called
    assert update_user_mock.called
