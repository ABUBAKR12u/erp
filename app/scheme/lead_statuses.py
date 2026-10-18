from pydantic import BaseModel, ConfigDict, Field, model_validator


class LeadStatusBase(BaseModel):
    name: str = Field(min_length=1, max_length=60)
    is_won: bool = False
    is_lost: bool = False


class LeadStatusAdd(LeadStatusBase):
    pass


class LeadStatusUpdate(LeadStatusBase):
    pass

class LeadStatusResponse(BaseModel):
    id: int
    name: str
    position: int
    is_won: bool
    is_lost: bool