from pydantic import BaseModel

class CreateUser(BaseModel):
    username: str
    password: str
    role: str

class LoginUser(BaseModel):
    username: str
    password: str
    role: str

class MeToken(BaseModel):
    token: str