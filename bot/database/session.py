from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from config import config

DATABASE_URL = (
    f"postgresql+asyncpg://{config.db_user}:{config.db_password}"
    f"@{config.db_host}:{config.db_port}/{config.db_name}"
)

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
