import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import logging

from services.postgres_crud.room_crud import create_initial_rooms
from services.mongo_database import MongoDatabase
from services.postgres_database import PostgresDatabase
from config.config import config
from handlers.user.start import start_router
from handlers.user.booking import booking_router
from handlers.admin.auth import auth_router
from handlers.admin.reviews import reviews_router
from handlers.admin.rooms import admin_rooms_router
from handlers.user.feedback import feedback_router
from middlewares.db_session import DBSessionMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("feedback.log"),
        logging.StreamHandler()
    ]
)

async def main():
    logging.basicConfig(level=logging.INFO)
    
    bot = Bot(token=config.BOT_TOKEN.get_secret_value())
    dp = Dispatcher(storage=MemoryStorage())

    postgres_db = PostgresDatabase()
    mongo_db = MongoDatabase()
    
    try:
        await mongo_db.connect()
        await mongo_db.init_indexes()
        await postgres_db.create_tables()
        
        dp.message.middleware(DBSessionMiddleware(postgres_db.async_session_maker))
        dp.callback_query.middleware(DBSessionMiddleware(postgres_db.async_session_maker))
        
        async with postgres_db.session_scope() as session:
            await create_initial_rooms(session)
        
        dp.include_router(start_router)
        dp.include_router(auth_router)
        dp.include_router(feedback_router)
        dp.include_router(reviews_router)
        dp.include_router(booking_router)
        dp.include_router(admin_rooms_router)

        dp["postgres_db"] = postgres_db
        dp["mongo_db"] = mongo_db
        
        

        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())

