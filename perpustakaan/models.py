from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Player(Base):
    __tablename__ = 'players'

    id = Column(Integer, primary_key=True)
    nama = Column(String,  nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)

    loans = relationship("Loan", back_populates="player")

class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    nomer_buku = Column(String, nullable=False, unique=True)
    judul = Column(String, nullable=False)
    penulis = Column(String, nullable=False)
    tahun_terbit = Column(Integer, nullable=False)
    status = Column(String, nullable=False, default='available')

    loans = relationship("Loan", back_populates="book")

class Loan(Base):
    __tablename__ = 'loans'

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    tanggal_pinjam = Column(DateTime, default=datetime.utcnow())
    rencana_kembali = Column(DateTime, nullable=True)
    tanggal_kembali = Column(DateTime, nullable=True)

    player = relationship("Player", back_populates="loans")
    book = relationship("Book", back_populates="loans")