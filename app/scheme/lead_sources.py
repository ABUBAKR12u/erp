from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class LeadSourceBase(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    monthly_budget: Decimal | None = Field(default=0, ge=0, max_digits=14, decimal_places=2)



class LeadSourceAdd(LeadSourceBase):
    pass


class LeadSourceUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    monthly_budget: Decimal | None = Field(default=0, ge=0, max_digits=14, decimal_places=2)

class LeadSourceResponse(BaseModel):
    id: int
    name:str
    monthly_budget:Decimal
    is_active: bool
