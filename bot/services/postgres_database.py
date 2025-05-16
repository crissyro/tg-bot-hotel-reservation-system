from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from config.config import config
import asyncpg

Base = declarative_base()

class Database:
    def __init__(self):
        self.engine = create_async_engine(
            f"postgresql+asyncpg://{config.postgres_user}:{config.postgres_password.get_secret_value()}"
            f"@{config.postgres_host}:{config.postgres_port}/{config.postgres_db}",
            echo=True
        )
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def connect(self):
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            print("✅ PostgreSQL connected")
        except asyncpg.exceptions.PostgresError as e:
            print(f"❌ PostgreSQL connection error: {e}")

    async def get_session(self):
        async with self.async_session() as session:
            yield session