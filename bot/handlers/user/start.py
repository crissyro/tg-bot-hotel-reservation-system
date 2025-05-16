from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from keyboards.user import main_keyboard

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "🏨 Добро пожаловать в <b>Luxury Hotel Bot</b>!\n\n"
        "Здесь вы можете:\n"
        "• 🛌 Забронировать номер\n"
        "• 🍽 Заказать из ресторана\n"
        "• 🍹 Сделать заказ в баре\n"
        "• 📝 Оставить отзыв\n\n"
        "Выберите действие:",
        reply_markup=main_keyboard(),
        parse_mode="HTML"
    )