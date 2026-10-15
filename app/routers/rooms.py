from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select

from app.database.Base import MyDb
from app.model.branches import Branch
from app.model.rooms import Room
from app.scheme.rooms import RoomAdd, RoomResponse
from app.utils.checker import check_ident
from app.utils.security import get_current_user

router = APIRouter(tags=["Rooms"], prefix="/rooms")

@router.post("/")
async def add_room(room: RoomAdd , db: MyDb , current_user=Depends(get_current_user)):
    await check_ident(db , Branch , room.branch_id)
    obj = Room(
        **room.model_dump()
    )
    db.add(obj)
    await db.commit()
    return {"msg": "Room added successfully"}

@router.get("/" , response_model=List[RoomResponse])
async def list_rooms(db: MyDb , is_active:bool=True,name: str = None):
    result = select(Room)
    if name:
        result = result.where(Room.name.ilike(f"%{name}%"))
    if is_active is not None:
        result = result.where(Room.is_active==is_active)

    find = await db.execute(result)

    return find.scalars().all()


@router.delete("/{room_id}")
async def delete_room(room_id: int,db: MyDb):
    room =await check_ident(db , Room , room_id)
    room.is_active = False
    await db.commit()
    return {"msg": "Room deleted successfully"}
