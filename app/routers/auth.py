from fastapi import APIRouter, Depends, HTTPException , Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from app.database.Base import MyDb
from app.model.employees import Employees
from app.scheme.auth import Auth
from app.utils.rate_limiting import limiter_by_ip_address
from app.utils.security import create_access_token, create_refresh_token, verify_password, create_new_token

router = APIRouter(tags=["Auth"], prefix="/auth")


@router.post("/login")
@limiter_by_ip_address.limit("5/minutes")
async def login(request: Request ,db:MyDb , user_data:OAuth2PasswordRequestForm=Depends()):
    result=await db.execute(select(Employees).where(Employees.phone==user_data.username))
    employee=result.scalars().first()
    if not employee:
        raise HTTPException(401, "Incorrect username or password")
    if not await verify_password(user_data.password , employee.password):
        raise HTTPException(401, "Incorrect username or password")
    access_token=await create_access_token(employee.id)
    refresh_token=await create_refresh_token(employee.id)
    return {"access_token":access_token,"refresh_token":refresh_token}

@router.post("/refresh")
async def refresh_token(token: Auth,db:MyDb):
     return await create_new_token(token.refresh_token,db)
