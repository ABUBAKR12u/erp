from pydantic import BaseModel, ConfigDict


class RoleBase(BaseModel):
    code: str
    name: str


class RoleAdd(RoleBase):
    pass

class RoleUpdate(RoleBase):
    pass

class RoleResponse(BaseModel):
    id:int
    code: str
    name: str
    is_system: bool
    model_config = ConfigDict(from_attributes=True)