from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    nama: str
    email: str
    password: str
    alamat: Optional[str] = None
    photo: Optional[str] = None
    bio: Optional[str] = None