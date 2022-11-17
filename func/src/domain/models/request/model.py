from typing import Optional, Dict, Any

from pydantic import BaseModel, root_validator

from src.domain.models.jwt_data.model import Jwt


class CompanyDirectorModel(BaseModel):
    is_company_director: bool
    company_name: Optional[str]
    company_ticker: Optional[str]

    @root_validator()
    def validate_composition(cls, values: Dict[str, Any]):
        is_company_director = values.get("is_company_director")
        if not is_company_director:
            values["company_name"] = None
            values["company_ticker"] = None
            return values

        company_name = values.get("company_name")
        company_ticker = values.get("company_ticker")
        if is_company_director and (not company_name or not company_ticker):
            raise ValueError(
                "You need to inform the field campany_name and company_ticker if you are a company director"
            )
        return values


class CompanyDirectorRequest:
    def __init__(
        self,
        x_thebes_answer: str,
        unique_id: str,
        company_director: CompanyDirectorModel,
    ):
        self.x_thebes_answer = x_thebes_answer
        self.unique_id = unique_id
        self.company_director = company_director

    @classmethod
    async def build(cls, x_thebes_answer: str, parameters: dict):
        jwt = await Jwt.build(jwt=x_thebes_answer)
        company_director = CompanyDirectorModel(**parameters)
        return cls(
            x_thebes_answer=x_thebes_answer,
            unique_id=jwt.unique_id,
            company_director=company_director,
        )
