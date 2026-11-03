from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from app.database.Base import MyDb
from app.model.branches import Branch
from app.model.rooms import Room
from app.scheme.rooms import RoomAdd, RoomResponse, RoomUpdate
from app.model.groups import Group
from app.utils.checker import check_ident
from app.utils.security import get_current_user, require_role

router = APIRouter(tags=["Rooms"], prefix="/rooms")

@router.post("/")
async def add_room(room: RoomAdd , db: MyDb , current_user=Depends(require_role("admin", "boss"))):
    await check_ident(db , Branch , room.branch_id)
    if room.branch_id!=current_user.branch_id and not current_user.is_superadmin and not any(er.role.code == "boss" for er in current_user.employee_role):
        raise HTTPException(403,"You are not allowed to add a room to this branch")
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


@router.put("/{room_id}")
async def update_room(room_id: int, room: RoomUpdate, db: MyDb, current_user=Depends(require_role("admin", "boss"))):
    obj = await check_ident(db, Room, room_id)
    await check_ident(db, Branch, room.branch_id)
    if not current_user.is_superadmin and not any(er.role.code == "boss" for er in current_user.employee_role) and (obj.branch_id != current_user.branch_id or room.branch_id != current_user.branch_id):
        raise HTTPException(403, "Bu filialga ruxsatingiz yo'q")
    groups = (await db.execute(select(Group).where(Group.room_id == room_id))).scalars().all()
    if groups and obj.branch_id != room.branch_id:
        raise HTTPException(409, "Guruhlari bor xonaning filialini almashtirib bo'lmaydi")
    if any(group.max_students > room.capacity for group in groups):
        raise HTTPException(409, "Xona sig'imi mavjud guruhlar chegarasidan kichik")
    for field, value in room.model_dump().items():
        setattr(obj, field, value)
    await db.commit()
    return {"msg": "Room updated successfully"}


@router.delete("/{room_id}")
async def delete_room(room_id: int,db: MyDb , current_user=Depends(require_role("admin","boss"))):
    room =await check_ident(db , Room , room_id)
    room.is_active = False
    await db.commit()
    return {"msg": "Room deleted successfully"}
