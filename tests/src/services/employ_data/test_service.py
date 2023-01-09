from unittest.mock import patch

import pytest
from decouple import Config
from persephone_client import Persephone

from func.src.domain.exceptions.model import InternalServerError, InvalidStepError
from func.src.domain.models.request.model import CompanyDirectorModel, CompanyDirectorRequest
from func.src.domain.models.user_data.company_director.model import CompanyDirectorData
from func.src.domain.models.user_data.device_info.model import DeviceInfo
from func.src.domain.models.user_data.onboarding_step.model import UserOnboardingStep
from func.src.transport.user_step.transport import StepChecker
from func.src.repositories.user.repository import UserRepository
from func.src.services.company_data.service import CompanyDataService

company_director_model_dummy = CompanyDirectorModel(
    **{"is_company_director": True, "company_name": "Lalau", "company_ticker": "LALA4"}
)
stub_device_info = DeviceInfo({"precision": 1}, "")

company_director_request_dummy = CompanyDirectorRequest(
    x_thebes_answer="x_thebes_answer",
    unique_id="unique_id",
    company_director=company_director_model_dummy,
    device_info=stub_device_info
)
company_director_data_dummy = CompanyDirectorData(
    unique_id=company_director_request_dummy.unique_id,
    is_company_director=company_director_model_dummy.is_company_director,
    company_name=company_director_model_dummy.company_name,
    company_ticker=company_director_model_dummy.company_ticker,
)
onboarding_step_correct_stub = UserOnboardingStep("finished", "company_director")
onboarding_step_incorrect_stub = UserOnboardingStep("finished", "some_step")


def test___model_company_director_data_to_persephone():
    result = CompanyDataService._CompanyDataService__model_company_director_data_to_persephone(
        company_director_data_dummy,
        stub_device_info
    )
    expected_result = {
        "unique_id": company_director_data_dummy.unique_id,
        "company_director": company_director_data_dummy.is_company_director,
        "user_is_company_director_of": company_director_data_dummy.company_name,
        "company_ticker_that_user_is_director_of": company_director_data_dummy.company_ticker,
        "device_info": stub_device_info.device_info,
        "device_id": stub_device_info.device_id
    }
    assert result == expected_result


@pytest.mark.asyncio
@patch.object(Config, "__call__")
@patch.object(UserRepository, "update_user")
@patch.object(Persephone, "send_to_persephone")
@patch.object(StepChecker, "get_onboarding_step")
async def test_update_company_director_data_for_us(
    get_onboarding_step_mock, persephone_client_mock, update_user_mock, mocked_env
):
    get_onboarding_step_mock.return_value = onboarding_step_correct_stub
    persephone_client_mock.return_value = (True, 0)
    update_user_mock.return_value = True
    result = await CompanyDataService.update_company_director_data_for_us(
        company_director_request_dummy
    )
    expected_result = None

    assert result == expected_result
    assert get_onboarding_step_mock.called
    assert persephone_client_mock.called
    assert update_user_mock.called


@pytest.mark.asyncio
@patch.object(Config, "__call__")
@patch.object(UserRepository, "update_user")
@patch.object(Persephone, "send_to_persephone")
@patch.object(StepChecker, "get_onboarding_step")
async def test_update_company_director_data_for_us_when_user_is_in_wrong_step(
    get_onboarding_step_mock, persephone_client_mock, update_user_mock, mocked_env
):
    get_onboarding_step_mock.return_value = onboarding_step_incorrect_stub
    persephone_client_mock.return_value = (True, 0)
    update_user_mock.return_value = True
    with pytest.raises(InvalidStepError):
        result = await CompanyDataService.update_company_director_data_for_us(
            company_director_request_dummy
        )

    assert get_onboarding_step_mock.called
    assert not persephone_client_mock.called
    assert not update_user_mock.called


@pytest.mark.asyncio
@patch.object(Config, "__call__")
@patch.object(UserRepository, "update_user")
@patch.object(Persephone, "send_to_persephone")
@patch.object(StepChecker, "get_onboarding_step")
async def test_update_company_director_data_for_us_when_cant_send_to_persephone(
    get_onboarding_step_mock, persephone_client_mock, update_user_mock, mocked_env
):
    get_onboarding_step_mock.return_value = onboarding_step_correct_stub
    persephone_client_mock.return_value = (False, 0)
    update_user_mock.return_value = True
    with pytest.raises(InternalServerError):
        result = await CompanyDataService.update_company_director_data_for_us(
            company_director_request_dummy
        )

    assert get_onboarding_step_mock.called
    assert persephone_client_mock.called
    assert not update_user_mock.called


@pytest.mark.asyncio
@patch.object(Config, "__call__")
@patch.object(UserRepository, "update_user")
@patch.object(Persephone, "send_to_persephone")
@patch.object(StepChecker, "get_onboarding_step")
async def test_update_company_director_data_for_us_when_cant_update_user_register(
    get_onboarding_step_mock, persephone_client_mock, update_user_mock, mocked_env
):
    get_onboarding_step_mock.return_value = onboarding_step_correct_stub
    persephone_client_mock.return_value = (True, 0)
    update_user_mock.return_value = False
    with pytest.raises(InternalServerError):
        result = await CompanyDataService.update_company_director_data_for_us(
            company_director_request_dummy
        )

    assert get_onboarding_step_mock.called
    assert persephone_client_mock.called
    assert update_user_mock.called
