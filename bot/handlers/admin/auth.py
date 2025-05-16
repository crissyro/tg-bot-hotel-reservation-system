from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from config.config import config
from keyboards.admin import admin_panel_keyboard

router = Router()

class AdminAuth(StatesGroup):
    waiting_password = State()

@router.message(Command("admin_input"))
async def admin_login(message: types.Message, state: FSMContext):
    if message.from_user.id not in config.admins:
        await message.answer("⛔ Доступ запрещен!")
        return
        
    await message.answer(
        "🔐 <b>Административная панель</b>\n"
        "Введите пароль для доступа:",
        parse_mode="HTML"
    )
    await state.set_state(AdminAuth.waiting_password)

async def show_admin_panel(message: types.Message):
    await message.answer(
        "⚙️ <b>Административная панель</b>\n"
        "Выберите раздел для управления:",
        reply_markup=admin_panel_keyboard(),
        parse_mode="HTML"
    )
    
    await message.answer(
        "⌨️ Переключение на админ-клавиатуру...",
        reply_markup=types.ReplyKeyboardRemove()
    )

@router.message(AdminAuth.waiting_password, F.text)
async def admin_password_check(message: types.Message, state: FSMContext):
    if message.text == config.admin_password:
        await message.answer("✅ Успешная авторизация!")
        await show_admin_panel(message)
        await state.clear()
    else:
        await message.answer("❌ Неверный пароль! Попробуйте еще раз:")