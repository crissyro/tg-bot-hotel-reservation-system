import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import logging

from config.config import config
from handlers.user.start import router as user_router
from handlers.admin.auth import router as admin_router


async def main():
    logging.basicConfig(level=logging.INFO)
    
    bot = Bot(token=config.bot_token.get_secret_value())
    dp = Dispatcher(storage=MemoryStorage())
    
    dp.include_router(user_router)
    dp.include_router(admin_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
