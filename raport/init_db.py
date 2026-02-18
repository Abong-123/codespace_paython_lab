import asyncio
from database import engine, Base
import models

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("tabel monitorings berhasil dibuat!")

if __name__ == "__main__":
    asyncio.run(init_db())