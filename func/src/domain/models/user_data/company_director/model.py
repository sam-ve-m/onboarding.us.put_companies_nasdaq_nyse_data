from typing import Optional

from func.src.domain.models.user_data.model import UserData


class CompanyDirectorData(UserData):
    def __init__(
        self,
        unique_id: str,
        is_company_director: bool,
        company_name: Optional[str],
        company_ticker: Optional[str],
    ):
        self.unique_id = unique_id
        self.is_company_director = is_company_director
        self.company_name = company_name
        self.company_ticker = company_ticker

    def get_data_representation(self) -> dict:
        data = {
            "external_exchange_requirements.us.is_company_director": self.is_company_director,
            "external_exchange_requirements.us.is_company_director_of": self.company_name,
            "external_exchange_requirements.us.company_ticker_that_user_is_director_of": self.company_ticker,
        }
        return data
