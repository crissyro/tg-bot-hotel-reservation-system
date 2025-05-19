from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime
from keyboards.user import main_keyboard, back_keyboard
from services.postgres_crud.room_crud import RoomCRUD
from services.postgres_crud.booking_crud import BookingCRUD
from services.postgres_crud.user_crud import UserCRUD
from aiogram.fsm.state import State, StatesGroup

class BookingFSM(StatesGroup):
    choosing_dates = State()
    selecting_room = State()
    confirming_booking = State()
    
booking_router = Router()
async def validate_date(date_str: str) -> datetime | None:
    try:
        return datetime.strptime(date_str, "%d.%m.%Y")
    except ValueError:
        return None

@booking_router.message(F.text == "🛎 Бронирование")
async def start_booking(message: Message, state: FSMContext):
    await message.answer(
        "\U0001F4C5 Введите дату заезда в формате <b>ДД.MM.ГГГГ</b>:\n\nНапример: 25.05.2025",
        reply_markup=back_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(BookingFSM.choosing_dates)
    await state.update_data(check_in=None)

@booking_router.message(BookingFSM.choosing_dates)
async def choose_dates(message: Message, state: FSMContext, **kwargs):
    session = kwargs.get("session")
    if session is None:
        await message.answer("❌ Ошибка сервера: нет подключения к базе данных.")
        return

    state_data = await state.get_data()
    date = await validate_date(message.text)

    if not date:
        await message.answer("❌ Неверный формат даты! Используйте ДД.MM.ГГГГ")
        return

    if not state_data.get("check_in"):
        await state.update_data(check_in=date)
        await message.answer("📅 Введите дату выезда в формате ДД.MM.ГГГГ:")
        return

    check_in = state_data["check_in"]
    if date <= check_in:
        await message.answer("❗ Дата выезда должна быть позже даты заезда")
        return

    room_crud = RoomCRUD(session)
    available_rooms = await room_crud.get_available_rooms(check_in, date)

    if not available_rooms:
        await message.answer("😕 Нет доступных номеров на выбранные даты")
        await state.clear()
        return

    builder = InlineKeyboardBuilder()
    for room in available_rooms:
        builder.button(text=f"{room.human_name} - {room.price}₽", callback_data=f"select_{room.id}")
    builder.button(text="🔙 Назад", callback_data="back_dates")

    await state.update_data(check_out=date, rooms=[r.id for r in available_rooms])
    await message.answer("🏨 Выберите номер:", reply_markup=builder.as_markup())
    await state.set_state(BookingFSM.selecting_room)

@booking_router.callback_query(F.data.startswith("select_"))
async def select_room(callback: CallbackQuery, state: FSMContext):
    room_id = int(callback.data.split("_")[1])
    await state.update_data(selected_room=room_id)

    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Подтвердить", callback_data="confirm_booking")
    builder.button(text="🔙 Назад", callback_data="back_to_rooms")

    await callback.message.edit_text(
        "Подтвердите бронирование этого номера:",
        reply_markup=builder.as_markup()
    )
    await state.set_state(BookingFSM.confirming_booking)

@booking_router.callback_query(F.data == "confirm_booking")
async def confirm_booking(callback: CallbackQuery, state: FSMContext, session):
    
    data = await state.get_data()
    user_crud = UserCRUD(session)
    booking_crud = BookingCRUD(session)

    user = await user_crud.get_or_create_user(
        telegram_id=callback.from_user.id,
        name=callback.from_user.first_name,
        surname=callback.from_user.last_name or ""
    )

    room = await RoomCRUD(session).get_room_by_id(data["selected_room"])
    days = (data["check_out"] - data["check_in"]).days
    total_price = room.price * days

    booking = await booking_crud.create_booking(
        total_price=total_price,
        user_id=user.id,
        room_id=room.id,
        check_in=data["check_in"],
        check_out=data["check_out"]
    )

    check_in_str = data["check_in"].strftime("%d.%m.%Y")
    check_out_str = data["check_out"].strftime("%d.%m.%Y")

    await callback.message.edit_text(
        f"✅ Бронирование подтверждено!\n\n"
        f"🏨 Номер: {room.human_name}\n"
        f"📅 Заезд: {check_in_str}\n"
        f"📅 Выезд: {check_out_str}\n"
        f"💰 Итого: {total_price}₽"
    )
    await state.clear()

@booking_router.message(F.text == "🔙 Назад")
async def back_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()

    if current_state == BookingFSM.selecting_room.state:
        await state.set_state(BookingFSM.choosing_dates)
        await message.answer(
            "📅 Введите дату заезда в формате <b>ДД.MM.ГГГГ</b>:",
            reply_markup=back_keyboard(),
            parse_mode="HTML"
        )
    elif current_state == BookingFSM.confirming_booking.state:
        await state.set_state(BookingFSM.selecting_room)
        await message.answer("🏨 Выберите номер:", reply_markup=back_keyboard())
    else:
        await message.answer("🔙 Вы уже на начальном этапе.", reply_markup=main_keyboard())

@booking_router.message(F.text == "❌ Отмена")
async def cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Бронирование отменено.", reply_markup=main_keyboard())
