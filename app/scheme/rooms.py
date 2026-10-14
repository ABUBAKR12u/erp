from pydantic import BaseModel

class RoomBase(BaseModel):
    branch_id: int
    name: str
    capacity: int

class RoomAdd(RoomBase):
    pass

class RoomUpdate(RoomBase):
    pass

class RoomResponse(BaseModel):
    id:int
    branch_id: int
    name: str
    capacity: int
    is_active: bool
