import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import joinedload
from models.postgres_models import Booking
from keyboards.user import main_keyboard, back_keyboard
from services.postgres_crud.room_crud import RoomCRUD
from services.postgres_crud.booking_crud import BookingCRUD
from services.postgres_crud.user_crud import UserCRUD
from aiogram.fsm.state import State, StatesGroup

class BookingFSM(StatesGroup):
    choosing_dates = State()
    selecting_room = State()
    confirming_booking = State()
    choosing_booking_to_pay = State()
    choosing_payment_method = State()
    
booking_router = Router()

@booking_router.message(F.text == "↩️ Главное меню")
async def back_to_main_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Вы вернулись в главное меню.", reply_markup=main_keyboard())
    
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
        await message.answer("❌ Ошибка сервера: нет подключения к базе данных.", reply_markup=back_keyboard())
        return

    state_data = await state.get_data()
    date = await validate_date(message.text)

    if not date:
        await message.answer("❌ Неверный формат даты! Используйте ДД.MM.ГГГГ", reply_markup=back_keyboard())
        return

    if not state_data.get("check_in"):
        await state.update_data(check_in=date)
        await message.answer("📅 Введите дату выезда в формате ДД.MM.ГГГГ:", reply_markup=back_keyboard())
        return

    check_in = state_data["check_in"]
    if date <= check_in:
        await message.answer("❗ Дата выезда должна быть позже даты заезда", reply_markup=back_keyboard())
        return

    room_crud = RoomCRUD(session)
    available_rooms = await room_crud.get_available_rooms(check_in, date)

    if not available_rooms:
        await message.answer("😕 Нет доступных номеров на выбранные даты", reply_markup=back_keyboard())
        await state.clear()
        return

    builder = InlineKeyboardBuilder()
    for i, room in enumerate(available_rooms, 1):
        builder.button(text=f"{room.human_name} - {room.price}₽", callback_data=f"select_{room.id}")
        if i % 2 == 0:
            builder.row()  

    await state.update_data(check_out=date, rooms=[r.id for r in available_rooms])
    await message.answer("🏨 Выберите номер:", reply_markup=builder.as_markup())
    await state.set_state(BookingFSM.selecting_room)

@booking_router.callback_query(F.data.startswith("select_"))
async def select_room(callback: CallbackQuery, state: FSMContext):
    room_id = int(callback.data.split("_")[1])
    await state.update_data(selected_room=room_id)

    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Подтвердить бронирование", callback_data="confirm_booking")
    builder.button(text="❌ Отмена", callback_data="cancel_booking")
    builder.row()

    await callback.message.edit_text("Вы выбрали номер. Подтвердите бронирование или отмените:", reply_markup=builder.as_markup())
    
async def cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Бронирование отменено.", reply_markup=main_keyboard())
    
@booking_router.callback_query(F.data == "confirm_booking")
async def confirm_booking(callback: CallbackQuery, state: FSMContext, session):
    data = await state.get_data()
    user_crud = UserCRUD(session)
    booking_crud = BookingCRUD(session)
    room_crud = RoomCRUD(session)
    logging.info(f"Поиск пользователя: {callback.from_user.id}")
    user = await user_crud.get_user_by_telegram_id(callback.from_user.id)
    logging.info(f"Результат: {user}")
    if not user:
        user = await user_crud.create_user(
            telegram_id=callback.from_user.id,
            name=callback.from_user.first_name or "Неизвестный",
            surname=callback.from_user.last_name or "Пользователь"
        )

    room = await room_crud.get_room_by_id(data["selected_room"])
    if not room:
        await callback.answer("❌ Номер не найден!")
        return

    days = (data["check_out"] - data["check_in"]).days
    total_price = room.price * days

    booking = await booking_crud.create_booking(
        total_price=total_price,
        user_id=user.id,
        room_id=room.id,
        check_in=data["check_in"],
        check_out=data["check_out"]
    )

    await room_crud.refresh_rooms_availability()
    await room_crud.auto_update_statuses()

    check_in_str = data["check_in"].strftime("%d.%m.%Y")
    check_out_str = data["check_out"].strftime("%d.%m.%Y")
    await callback.message.edit_text(
        f"✅ Бронирование подтверждено!\n\n"
        f"🏨 Номер: {room.human_name}\n"
        f"📅 Заезд: {check_in_str}\n"
        f"📅 Выезд: {check_out_str}\n"
        f"💰 Итого: {total_price}₽"
    )
    
    await callback.message.answer(
    "Вы вернулись в главное меню.",
    reply_markup=main_keyboard()
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

@booking_router.message(F.text == "💳 Оплатить бронь")
async def pay_booking_start(message: Message, state: FSMContext, session):
    user_crud = UserCRUD(session)
    user = await user_crud.get_user_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer("❌ Вы не зарегистрированы в системе.", reply_markup=main_keyboard())
        return

    booking_crud = BookingCRUD(session)
    bookings = await booking_crud.get_unpaid_bookings_by_user_id(user.id)

    if not bookings:
        await message.answer("💳 У вас нет броней для оплаты.", reply_markup=main_keyboard())
        return

    stmt = (
        select(Booking)
        .where(Booking.user_id == user.id)
        .options(joinedload(Booking.room))  
    )
    result = await session.execute(stmt)
    bookings = result.unique().scalars().all()

    builder = InlineKeyboardBuilder()
    for b in bookings:
        check_in = b.check_in.strftime("%d.%m.%Y")
        check_out = b.check_out.strftime("%d.%m.%Y")
        builder.button(
            text=f"№{b.id}: {b.room.human_name} с {check_in} по {check_out} — {b.total_price}₽",
            callback_data=f"pay_{b.id}"
        )
    builder.button(text="↩️ Главное меню", callback_data="pay_back")
    await message.answer("Выберите бронь для оплаты:", reply_markup=builder.as_markup())
    await state.set_state(BookingFSM.choosing_booking_to_pay)

@booking_router.callback_query(F.data.startswith("pay_"), BookingFSM.choosing_booking_to_pay)
async def pay_booking_select(callback: CallbackQuery, state: FSMContext):
    booking_id = int(callback.data.split("_")[1])
    await state.update_data(booking_id=booking_id)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💳 Карта", callback_data="method_card"),
            InlineKeyboardButton(text="🪙 Биткоин", callback_data="method_bitcoin"),
            InlineKeyboardButton(text="🏦 СберПей", callback_data="method_sberpay"),
        ],
        [InlineKeyboardButton(text="↩️ Отмена", callback_data="pay_cancel")]
    ])
    await callback.message.edit_text("Выберите способ оплаты:", reply_markup=keyboard)
    await state.set_state(BookingFSM.choosing_payment_method)

@booking_router.callback_query(F.data.startswith("method_"), BookingFSM.choosing_payment_method)
async def pay_booking_method_selected(callback: CallbackQuery, state: FSMContext, session):
    data = await state.get_data()
    booking_id = data.get("booking_id")
    payment_method = callback.data.split("_")[1]

    booking_crud = BookingCRUD(session)
    await booking_crud.mark_as_paid(booking_id)

    await callback.message.edit_text(
        f"✅ Оплата брони №{booking_id} успешно проведена через {payment_method.capitalize()}!\n"
        "Спасибо за оплату.",
        reply_markup=None  
    )
    await state.clear()
@booking_router.callback_query(F.data == "pay_back", BookingFSM.choosing_booking_to_pay)
async def pay_back_to_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Вы вернулись в главное меню.", reply_markup=main_keyboard())

@booking_router.callback_query(F.data == "pay_cancel", BookingFSM.choosing_payment_method)
async def pay_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Оплата отменена.", reply_markup=main_keyboard())
    
@booking_router.message(F.text == "❌ Отменить бронь")
async def cancel_booking_start(message: Message, state: FSMContext, session):
    user_crud = UserCRUD(session)
    user = await user_crud.get_user_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer("❌ Вы не зарегистрированы в системе.", reply_markup=main_keyboard())
        return

    booking_crud = BookingCRUD(session)
    bookings = await booking_crud.get_active_bookings_by_user_id(user.id)  

    if not bookings:
        await message.answer("❌ У вас нет активных бронирований для отмены.", reply_markup=main_keyboard())
        return

    builder = InlineKeyboardBuilder()
    for b in bookings:
        check_in = b.check_in.strftime("%d.%m.%Y")
        check_out = b.check_out.strftime("%d.%m.%Y")
        builder.button(
            text=f"№{b.id}: {b.room.human_name} с {check_in} по {check_out} (Отменить)",
            callback_data=f"cancel_{b.id}"
        )
    builder.button(text="↩️ Главное меню", callback_data="cancel_back")
    await message.answer("Выберите бронирование для отмены:", reply_markup=builder.as_markup())
    await state.set_state(BookingFSM.choosing_booking_to_pay)

@booking_router.callback_query(F.data.startswith("cancel_"))
async def cancel_booking_confirm(callback: CallbackQuery, state: FSMContext, session):
    try:
        booking_id = int(callback.data.split("_")[1])
        booking_crud = BookingCRUD(session)
        await booking_crud.cancel_booking(booking_id)
        await callback.message.edit_text(
            "✅ Бронирование отменено.",
            reply_markup=None  
        )
        await state.clear()
    except (IndexError, ValueError) as e:
        logging.error(f"Ошибка при отмене бронирования: {e}")
        await callback.answer("❌ Некорректный ID брони")

@booking_router.callback_query(F.data == "cancel_back")
async def cancel_back_to_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Вы вернулись в главное меню.", reply_markup=main_keyboard())