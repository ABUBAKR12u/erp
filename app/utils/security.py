from datetime import datetime, timedelta, timezone
from encodings.punycode import selective_find

from fastapi import HTTPException
from jose import jwt, ExpiredSignatureError, JWTError
from dotenv import load_dotenv
import os
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.sql.functions import current_user

from app.database.Base import MyDb
from app.model.employees import Employees

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM= os.getenv("ALGORITHM")

pwd_context = CryptContext(schemes=["argon2"])

async def hash_password(password):
    return pwd_context.hash(password)

async def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

async def create_access_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=16),
        "type":"access"
    }
    return jwt.encode(payload , SECRET_KEY ,algorithm=ALGORITHM)


async def create_refresh_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(days=3),
        "type":"refresh"
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

async def create_new_token(token:str, db):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload["type"] != "access":
            raise HTTPException(401,"No refresh token")
        user_id = payload["user_id"]
        result=await db.execute(select(Employees.id).where(Employees.id == user_id))
        user = result.scalars().first()
        if not user:
            raise HTTPException(404,"User not found")

        return {"your new access token ": await create_access_token(user)}
    except ExpiredSignatureError:
        raise HTTPException(401,"Token expired")
    except JWTError:
        raise HTTPException(401,"Token is invalid")
