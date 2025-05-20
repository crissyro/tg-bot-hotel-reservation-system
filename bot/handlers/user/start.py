from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from services.postgres_crud.user_crud import UserCRUD
from keyboards.user import main_keyboard

start_router = Router()

class Registration(StatesGroup):
    waiting_for_name = State()
    waiting_for_surname = State()


@start_router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext, session):
    user_crud = UserCRUD(session)
    await user_crud.get_or_create_user(
        telegram_id=message.from_user.id,
        name=message.from_user.first_name,
        surname=message.from_user.last_name or ""
    )
    
    await state.clear()
    await message.answer(
        "🏨 Добро пожаловать в <b>Luxury Hotel Bot</b>!\n\n"
        "Здесь вы можете:\n"
        "• 🛌 Забронировать номер\n"
        "• 📝 Оставить отзыв\n\n"
        "Выберите действие:",
        reply_markup=main_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(Registration.waiting_for_name)
    
@start_router.message(Registration.waiting_for_name, F.text)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Теперь укажите вашу фамилию:")
    await state.set_state(Registration.waiting_for_surname)

@start_router.message(Registration.waiting_for_surname, F.text)
async def process_surname(message: types.Message, state: FSMContext, session):
    data = await state.get_data()
    name = data.get("name")
    surname = message.text

    user_crud = UserCRUD(session)
    user = await user_crud.get_or_create_user(
        telegram_id=message.from_user.id,
        name=name,
        surname=surname
    )

    await state.clear()
    await message.answer(
        "✅ Регистрация завершена!\n"
        "Выберите действие:",
        reply_markup=main_keyboard(),
        parse_mode="HTML"
    )
    
@start_router.message(F.text == "📞 Контакты")
async def contacts_handler(message: types.Message):
    await message.answer(
        "🛎 <b>Наши контакты:</b>\n\n"
        "📍 Адрес: Улица Гостиничная, 1\n"
        "📱 Телефон: +7 (800) 555-35-35\n"
        "👨💻 Администратор: @raddan_mode\n\n"
        "⏰ Режим работы: круглосуточно",
        parse_mode="HTML"
    )

@start_router.message(F.text == "ℹ️ О нас")
async def about_handler(message: types.Message):
    await message.answer(
        "🏨 <b>Luxury Hotel — ваш идеальный отдых!</b>\n\n"
        "✨ Мы предлагаем:\n"
        "✅ Номера с видом на море\n"
        "✅ Ресторан высокой кухни\n"
        "✅ СПА-центр и бассейн\n"
        "✅ Конференц-залы\n\n"
        "🌟 Наши преимущества:\n"
        "• Бесплатный Wi-Fi\n"
        "• Круглосуточный сервис\n"
        "• Парковка для гостей\n"
        "• Детская комната\n\n"
        "💬 <i>Ваш комфорт — наш главный приоритет!</i>",
        parse_mode="HTML"
    )