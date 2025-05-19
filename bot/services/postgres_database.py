from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from config.config import config
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class PostgresDatabase:
    def __init__(self):
        self.engine = create_async_engine(config.postgres_url)
        self.async_session_maker = async_sessionmaker(
            self.engine, 
            expire_on_commit=False,
            autoflush=False
        )

    async def create_tables(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @asynccontextmanager
    async def session_scope(self):
        async with self.async_session_maker() as session:
            async with session.begin():  
                yield session