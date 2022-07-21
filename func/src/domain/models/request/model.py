from typing import Optional, Dict, Any

from pydantic import BaseModel, root_validator


class CompanyDirector(BaseModel):
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
