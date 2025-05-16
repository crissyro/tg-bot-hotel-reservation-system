import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import logging

from services.mongo_database import MongoDatabase
from services.postgres_database import Database
from config.config import config
from handlers.user.start import start_router
from handlers.admin.auth import auth_router
from handlers.user.feedback import feedback_router

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
    
    bot = Bot(token=config.bot_token.get_secret_value())
    dp = Dispatcher(storage=MemoryStorage())
    
    dp.include_router(start_router)
    dp.include_router(auth_router)
    dp.include_router(feedback_router)
    
    postgres_db = Database()
    mongo_db = MongoDatabase()
    
    await postgres_db.connect()
    await mongo_db.connect()

    start_router.postgres_db = postgres_db
    start_router.mongo_db = mongo_db
    auth_router.postgres_db = postgres_db
    auth_router.mongo_db = mongo_db


    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
