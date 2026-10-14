from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"])

async def hash_password(password):
    return pwd_context.hash(password)

async def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)