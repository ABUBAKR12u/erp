import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from dotenv import load_dotenv
from app.utils.config import settings

load_dotenv()

DB_USERNAME = settings.DB_USERNAME
DB_PASS=settings.DB_PASS
DB_NAME = settings.DB_NAME


engine = create_async_engine(f"mysql+aiomysql://{DB_USERNAME}:{DB_PASS}@localhost:3306/{DB_NAME}")
SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession)

async def get_db():
    async with SessionLocal() as db:
        yield db