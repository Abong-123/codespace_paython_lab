from fastapi import FastAPI, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db, Base, AsyncSessionLocal, engine
from models import SensorLog
from controller import ClimateController
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from bot.bot import send_telegram_message

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
controller = ClimateController()
jakarta_tz = timezone(timedelta(hours=7))

latest_data = {
    "temperature": None,
    "humidity": None,
    "fan": False,
    "heater": False
}

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "data": latest_data})

@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.post("/api/sensor")
async def receive_sensor_data(data: dict, db: AsyncSession = Depends(get_db)):
    temp = data["temperature"]
    humidity = data["humidity"]

    status_changed = controller.evaluate(temp)

    latest_data["temperature"] = temp
    latest_data["humidity"] = humidity
    latest_data["fan"] = controller.fan
    latest_data["heater"] = controller.heater

    if status_changed:
        if controller.fan:
            message = f"Temperature: {temp}°C, Humidity: {humidity}%, Fan: ON, Heater: OFF"
        elif controller.heater:
            message = f"Temperature: {temp}°C, Humidity: {humidity}%, Fan: OFF, Heater: ON"
        else:
            message = f"Suhu Normal: {temp}°C, Humidity: {humidity}%,"
        print(f"Status changed: Fan: {controller.fan}, Heater: {controller.heater}")
        await send_telegram_message(message)
        async with AsyncSessionLocal() as session:
            log = SensorLog(
                temperature=temp,
                humidity=humidity,
                fan=controller.fan,
                heater=controller.heater,
                timestamp=datetime.now(jakarta_tz)
            )
            session.add(log)
            await session.commit()
    return {"message": "Data received", "status": "success"}

@app.get("/api/status")
async def get_status(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SensorLog).order_by(SensorLog.timestamp.desc()).limit(1))
    latest = result.scalar_one_or_none()
    if latest:
        jakarta_time = latest.timestamp.astimezone(ZoneInfo("Asia/Jakarta")) if latest.timestamp else None
        return {
            "temperature": latest.temperature,
            "humidity": latest.humidity,
            "fan": latest.fan,
            "heater": latest.heater,
            "timestamp": jakarta_time.isoformat() if jakarta_time else None,
            "raw_timestamp": latest.timestamp,
            "raw_timezone": latest.timestamp.tzinfo if latest.timestamp else None
        }
    else:
        return {
            "temperature": None,
            "humidity": None,
            "fan": False,
            "heater": False,
            "timestamp": None
        }
