from typing import Optional, Dict, Any

from pydantic import BaseModel, root_validator

from func.src.domain.models.jwt_data.model import Jwt
from func.src.domain.models.user_data.device_info.model import DeviceInfo
from func.src.transport.device_info.transport import DeviceSecurity


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
        device_info: DeviceInfo,
        unique_id: str,
        company_director: CompanyDirectorModel,
    ):
        self.x_thebes_answer = x_thebes_answer
        self.device_info = device_info
        self.unique_id = unique_id
        self.company_director = company_director

    @classmethod
    async def build(cls, x_thebes_answer: str, x_device_info: str, parameters: dict):
        company_director = CompanyDirectorModel(**parameters)
        jwt = await Jwt.build(jwt=x_thebes_answer)
        device_info = await DeviceSecurity.get_device_info(x_device_info)

        return cls(
            x_thebes_answer=x_thebes_answer,
            device_info=device_info,
            unique_id=jwt.unique_id,
            company_director=company_director,
        )
