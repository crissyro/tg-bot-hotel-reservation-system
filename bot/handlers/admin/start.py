from aiogram import Router, F
from aiogram.types import Message

from config import config

router = Router()


@router.message(F.text == "/start")
async def admin_start_handler(message: Message):
    if message.from_user.id not in config.admins:
        return

    await message.answer(
        "<b>👑 Добро пожаловать, Администратор!</b>\n\n"
        "Вы можете:\n"
        "• 🛏 Управлять номерами (добавлять, менять статус)\n"
        "• 🍷 Изменять меню бара\n"
        "• 📬 Смотреть отзывы\n\n"
        "Введите /admin для перехода в панель управления."
    )
