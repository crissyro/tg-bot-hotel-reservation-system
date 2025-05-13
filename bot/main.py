import asyncio
from aiogram import Bot, Dispatcher

from config import config
from handlers.user import start as user_start
from handlers.admin import start as admin_start

dp = Dispatcher()
bot = Bot(token=config.bot_token.get_secret_value())


def setup_routers():
    dp.include_router(admin_start.router)
    dp.include_router(user_start.router)


async def main():
    setup_routers()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
