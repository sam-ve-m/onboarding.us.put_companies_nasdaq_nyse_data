from unittest.mock import patch

import pytest
from etria_logger import Gladsheim

from src.domain.exceptions.model import InvalidStepError
from src.transport.user_step.transport import StepChecker


class SessionMock:
    def __init__(self, response):
        self.response = response

    def get(self, *args, **kwargs):
        return self

    async def __aenter__(self):
        class Response:
            def __init__(self, response):
                self._json = response

            async def json(self):
                return self._json

        return Response(self.response)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return


@pytest.mark.asyncio
@patch.object(Gladsheim, "error")
@patch.object(StepChecker, "get_session")
async def test_validate_step_br_when_is_correct_step(
    get_session_mock, etria_error_mock
):
    steps_response_dummy = {"result": {"current_step": "finished"}}
    get_session_mock.return_value = SessionMock(steps_response_dummy)
    result = await StepChecker._get_step_br("x-thebes-answer")
    expected_result = True
    assert result == expected_result


@pytest.mark.asyncio
@patch.object(Gladsheim, "error")
@patch.object(StepChecker, "get_session")
async def test_validate_step_br_when_is_wrong_step(get_session_mock, etria_error_mock):
    steps_response_dummy = {"result": {"current_step": "some_step"}}
    get_session_mock.return_value = SessionMock(steps_response_dummy)
    result = await StepChecker._get_step_br("x-thebes-answer")
    expected_result = False
    assert result == expected_result


@pytest.mark.asyncio
@patch.object(Gladsheim, "error")
@patch.object(StepChecker, "get_session")
async def test_validate_step_br_when_exception_occurs(
    get_session_mock, etria_error_mock
):
    get_session_mock.side_effect = Exception()
    with pytest.raises(Exception):
        result = await StepChecker._get_step_br("x-thebes-answer")
    assert etria_error_mock.called


@pytest.mark.asyncio
@patch.object(Gladsheim, "error")
@patch.object(StepChecker, "get_session")
async def test_validate_step_us_when_is_correct_step(
    get_session_mock, etria_error_mock
):
    steps_response_dummy = {"result": {"current_step": "company_director"}}
    get_session_mock.return_value = SessionMock(steps_response_dummy)
    result = await StepChecker._get_step_us("x-thebes-answer")
    expected_result = True
    assert result == expected_result


@pytest.mark.asyncio
@patch.object(Gladsheim, "error")
@patch.object(StepChecker, "get_session")
async def test_validate_step_us_when_is_wrong_step(get_session_mock, etria_error_mock):
    steps_response_dummy = {"result": {"current_step": "some_step"}}
    get_session_mock.return_value = SessionMock(steps_response_dummy)
    result = await StepChecker._get_step_us("x-thebes-answer")
    expected_result = False
    assert result == expected_result


@pytest.mark.asyncio
@patch.object(Gladsheim, "error")
@patch.object(StepChecker, "get_session")
async def test_validate_step_us_when_exception_occurs(
    get_session_mock, etria_error_mock
):
    get_session_mock.side_effect = Exception()
    with pytest.raises(Exception):
        result = await StepChecker._get_step_us("x-thebes-answer")
    assert etria_error_mock.called


@pytest.mark.asyncio
@patch.object(StepChecker, "_get_step_br", return_value=True)
@patch.object(StepChecker, "_get_step_us", return_value=True)
async def test_validate_onboarding_step_when_all_steps_are_true(
    steps_br_mock, steps_us_mock
):
    result = await StepChecker.get_onboarding_step("x-thebes-answer")
    expected_result = None
    assert result == expected_result


@pytest.mark.asyncio
@patch.object(StepChecker, "_get_step_br", return_value=False)
@patch.object(StepChecker, "_get_step_us", return_value=True)
async def test_validate_onboarding_step_when_one_step_is_false(
    steps_br_mock, steps_us_mock
):
    with pytest.raises(InvalidStepError):
        result = await StepChecker.get_onboarding_step("x-thebes-answer")
