from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine, AsyncEngine
from api.models.base import Base
import os


db_url = os.getenv('DB_URI', '')

engine: AsyncEngine = create_async_engine(
  db_url, echo=False, connect_args=dict(connect_timeout=30),
  pool_recycle=280, pool_pre_ping=True,
)

session_maker = async_sessionmaker(
  bind=engine, class_=AsyncSession, expire_on_commit=False
)

async def create_db():
  global engine
  async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)
  
async def drop_db():
  global engine
  async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.drop_all)
    
async def close_db():
  global engine
  if engine is not None:
    await engine.dispose()
    engine = None
