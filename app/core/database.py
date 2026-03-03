from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings
import asyncio
engine = create_async_engine(settings.DATABASE_URL, future=True, echo=False)
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


# dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
