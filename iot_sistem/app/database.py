from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql+asyncpg://appuser:password@localhost:5432/appdb"

engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

if __name__ == "__main__":
    import asyncio
    async def test_connection():
        try:
            async with engine.begin() as conn:
                print("database terhubung")
        except Exception as e:
            print("error", e)
    asyncio.run(test_connection())