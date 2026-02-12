from pydantic import BaseModel, EmailStr
from typing import Optional

class PaymentCreate(BaseModel):
    bulan: str
    amount: float 

class UserCreate(BaseModel):
    username: str 
    email: EmailStr
    password: str 

class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = None

class PaymentUpdate(BaseModel):
    bulan: str | None = None
    amount: str | None = None
