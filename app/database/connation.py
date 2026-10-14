import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from dotenv import load_dotenv
load_dotenv()

DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASS=os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")


engine = create_async_engine(f"mysql+aiomysql://{DB_USERNAME}:{DB_PASS}@localhost:3306/{DB_NAME}")
SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession)

async def get_db():
    async with SessionLocal() as db:
        yield db