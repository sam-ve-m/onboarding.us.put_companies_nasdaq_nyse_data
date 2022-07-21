from decouple import config
from persephone_client import Persephone

from src.domain.enums.persephone_queue import PersephoneQueue
from src.domain.exceptions.model import InternalServerError
from src.domain.models.request.model import CompanyDirector
from src.repositories.step_validator.repository import StepValidator
from src.repositories.user.repository import UserRepository


class CompanyDataService:
    persephone_client = Persephone

    @staticmethod
    def __model_company_director_data_to_persephone(
        company_director: bool,
        user_is_company_director_of: str,
        company_ticker_that_user_is_director_of: str,
        unique_id: str,
    ) -> dict:
        data = {
            "unique_id": unique_id,
            "company_director": company_director,
            "user_is_company_director_of": user_is_company_director_of,
            "company_ticker_that_user_is_director_of": company_ticker_that_user_is_director_of,
        }
        return data

    @classmethod
    async def update_company_director_data_for_us(
        cls, company_director_data: CompanyDirector, payload: dict
    ) -> None:

        await StepValidator.validate_onboarding_step(
            x_thebes_answer=payload["x_thebes_answer"]
        )

        unique_id = payload["data"]["user"]["unique_id"]

        user_is_company_director = company_director_data.is_company_director
        user_is_company_director_of = company_director_data.company_name
        company_ticker_that_user_is_director_of = company_director_data.company_ticker

        (
            sent_to_persephone,
            status_sent_to_persephone,
        ) = await cls.persephone_client.send_to_persephone(
            topic=config("PERSEPHONE_TOPIC_USER"),
            partition=PersephoneQueue.USER_COMPANY_DIRECTOR_IN_US.value,
            message=cls.__model_company_director_data_to_persephone(
                company_director=user_is_company_director,
                user_is_company_director_of=user_is_company_director_of,
                company_ticker_that_user_is_director_of=company_ticker_that_user_is_director_of,
                unique_id=unique_id,
            ),
            schema_name="user_company_director_us_schema",
        )
        if sent_to_persephone is False:
            raise InternalServerError("Error sending data to Persephone")

        was_updated = await UserRepository.update_user(
            unique_id=unique_id,
            new={
                "external_exchange_requirements.us.is_company_director": user_is_company_director,
                "external_exchange_requirements.us.is_company_director_of": user_is_company_director_of,
                "external_exchange_requirements.us.company_ticker_that_user_is_director_of": company_ticker_that_user_is_director_of,
            },
        )
        if not was_updated:
            raise InternalServerError("Error updating user data")
