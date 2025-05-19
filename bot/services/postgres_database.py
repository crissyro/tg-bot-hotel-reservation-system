from contextlib import asynccontextmanager
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from config.config import config

Base = declarative_base()

class PostgresDatabase:
    def __init__(self):
        self.engine = create_async_engine(config.postgres_url)
        self.async_session = async_sessionmaker(
            self.engine, expire_on_commit=False
        )

    async def create_tables(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
    def get_session(self):
        return self.async_session()
    
    @asynccontextmanager
    async def session_scope(self):
        async with self.async_session() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise e