from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from config import config


POSTGRES_URL = (
    f"postgresql+asyncpg://{config.postgres_user}:{config.postgres_password.get_secret_value()}"
    f"@{config.postgres_host}:{config.postgres_port}/{config.postgres_db}"
)

engine = create_async_engine(
    POSTGRES_URL,
    echo=True,  # Логирование запросов (можно отключить в продакшене)
    future=True
)

async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)


async def get_db():
    """Генератор сессий для Dependency Injection"""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()