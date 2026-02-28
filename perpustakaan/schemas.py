from pydantic import BaseModel
from typing import Optional
from datetime import date

class PlayerCreate(BaseModel):
    nama: str
    email: str
    password: str

class BookCreate(BaseModel):
    nomer_buku: str
    judul: str
    penulis: str
    tahun_terbit: int
    status: Optional[str] = 'available'

class LoanCreate(BaseModel):
    player_id: int
    book_id: int
