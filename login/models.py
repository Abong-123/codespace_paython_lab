from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String, nullable=False)

    payments = relationship(
        "WaterPayment", 
        back_populates="user",
        cascade = "all, delete"
    )

    __table_args__ = (
        UniqueConstraint("username", "email"),
    )

class WaterPayment(Base):
    __tablename__ = "waterpayments"

    id = Column(Integer, primary_key=True, index=True)
    bulan = Column (String, nullable=False)
    amount = Column (Float, nullable=False)
    create_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="payments")