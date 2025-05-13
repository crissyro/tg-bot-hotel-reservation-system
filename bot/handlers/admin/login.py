from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from config import config

router = Router()


class AdminLogin(StatesGroup):
    waiting_for_password = State()


@router.message(Command("admin_input"))
async def ask_admin_password(message: Message, state: FSMContext):
    await state.set_state(AdminLogin.waiting_for_password)
    await message.answer("🔐 Пожалуйста, введите пароль администратора:")


@router.message(AdminLogin.waiting_for_password)
async def process_admin_password(message: Message, state: FSMContext):
    if message.text == config.admin_password:
        await message.answer("✅ Пароль верный! Добро пожаловать в меню администратора.")
        # тут можно показать инлайн-кнопки или меню
        await state.clear()
    else:
        await message.answer("❌ Неверный пароль. Попробуйте ещё раз или введите /start.")
        await state.clear()
