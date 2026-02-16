from sqlalchemy import Column, Integer, Float, Boolean, DateTime, func
from database import Base
from datetime import datetime, timezone, timedelta

jakarta_tz = timezone(timedelta(hours=7))

class SensorLog(Base):
    __tablename__ = "sensor_logs"

    id = Column(Integer, primary_key=True, index=True)
    temperature = Column(Float)
    humidity = Column(Float)
    fan = Column(Boolean, default=False)
    heater = Column(Boolean, default=False)
    timestamp = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
