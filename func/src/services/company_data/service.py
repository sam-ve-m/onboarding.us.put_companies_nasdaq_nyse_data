from decouple import config
from persephone_client import Persephone

from func.src.domain.enums.persephone_queue import PersephoneQueue
from func.src.domain.exceptions.model import InternalServerError, InvalidStepError
from func.src.domain.models.request.model import CompanyDirectorRequest
from func.src.domain.models.user_data.company_director.model import CompanyDirectorData
from func.src.domain.models.user_data.device_info.model import DeviceInfo
from func.src.transport.user_step.transport import StepChecker
from func.src.repositories.user.repository import UserRepository


class CompanyDataService:
    persephone_client = Persephone

    @staticmethod
    def __model_company_director_data_to_persephone(
        company_director_data: CompanyDirectorData, device_info: DeviceInfo
    ) -> dict:
        data = {
            "unique_id": company_director_data.unique_id,
            "company_director": company_director_data.is_company_director,
            "user_is_company_director_of": company_director_data.company_name,
            "company_ticker_that_user_is_director_of": company_director_data.company_ticker,
            "device_info": device_info.device_info,
            "device_id": device_info.device_id,
        }
        return data

    @classmethod
    async def update_company_director_data_for_us(
        cls, company_director_request: CompanyDirectorRequest
    ):

        user_step = await StepChecker.get_onboarding_step(
            x_thebes_answer=company_director_request.x_thebes_answer
        )
        if not user_step.is_in_correct_step():
            raise InvalidStepError(
                f"Step BR: {user_step.step_br} | Step US: {user_step.step_us}"
            )

        company_director = company_director_request.company_director
        company_director_data = CompanyDirectorData(
            unique_id=company_director_request.unique_id,
            is_company_director=company_director.is_company_director,
            company_name=company_director.company_name,
            company_ticker=company_director.company_ticker,
        )

        (
            sent_to_persephone,
            status_sent_to_persephone,
        ) = await cls.persephone_client.send_to_persephone(
            topic=config("PERSEPHONE_TOPIC_USER"),
            partition=PersephoneQueue.USER_COMPANY_DIRECTOR_IN_US.value,
            message=cls.__model_company_director_data_to_persephone(
                company_director_data=company_director_data,
                device_info=company_director_request.device_info,
            ),
            schema_name="user_company_director_us_schema",
        )
        if sent_to_persephone is False:
            raise InternalServerError("Error sending data to Persephone")

        user_has_been_updated = await UserRepository.update_user(
            user_data=company_director_data
        )
        if not user_has_been_updated:
            raise InternalServerError("Error updating user data")
