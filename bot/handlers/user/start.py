from aiogram import Router, F
from aiogram.types import Message

router = Router()


@router.message(F.text == "/start")
async def user_start_handler(message: Message):
    await message.answer(
        "<b>🏨 Добро пожаловать в отель-бот!</b>\n\n"
        "Вы можете:\n"
        "• 📅 Забронировать номер\n"
        "• 🍽 Заказать еду и напитки\n"
        "• 📝 Оставить отзыв (после посещения)\n\n"
        "Чтобы начать — введите /menu или воспользуйтесь кнопками 👇"
    )
