from pydantic import BaseModel

class Auth(BaseModel):
    refresh_token: str

