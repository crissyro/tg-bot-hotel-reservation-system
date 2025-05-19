import logging
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from datetime import datetime, timedelta
from models.postgres_models import RoomStatusEnum
from services.postgres_crud.booking_crud import BookingCRUD
from services.postgres_crud.room_crud import RoomCRUD
from services.postgres_database import PostgresDatabase
from keyboards.user import main_keyboard
from aiogram.utils.keyboard import InlineKeyboardBuilder

booking_router = Router()

class BookingStates(StatesGroup):
    CHOOSE_CHECKIN = State()
    CHOOSE_CHECKOUT = State()
    SELECT_ROOM = State()
    CONFIRM_BOOKING = State()
    PAYMENT = State()

def cancel_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Отменить бронирование", callback_data="cancel_booking_process")
    return builder.as_markup()

async def validate_date(date_str: str) -> datetime:
    try:
        date = datetime.strptime(date_str, "%d.%m.%Y").date()
        today = datetime.now().date()
        
        if date < today:
            raise ValueError("Дата не может быть в прошлом")
        if date > today + timedelta(days=365):
            raise ValueError("Максимальный срок бронирования - 1 год")
        return datetime.combine(date, datetime.min.time())
    except ValueError as e:
        raise ValueError(f"Ошибка даты: {str(e)}") from e

@booking_router.message(F.text == "🛎 Бронирование")
async def start_booking(message: types.Message, state: FSMContext):
    await state.set_state(BookingStates.CHOOSE_CHECKIN)
    await message.answer(
        "📅 Введите дату заезда в формате ДД.ММ.ГГГГ (например, 01.01.2024):",
        reply_markup=cancel_keyboard()
    )

@booking_router.message(BookingStates.CHOOSE_CHECKIN)
async def process_checkin(message: types.Message, state: FSMContext):
    try:
        checkin_date = await validate_date(message.text)
        await state.update_data(checkin=checkin_date)
        await state.set_state(BookingStates.CHOOSE_CHECKOUT)
        await message.answer(
            "📅 Введите дату выезда в формате ДД.ММ.ГГГГ:",
            reply_markup=cancel_keyboard()
        )
    except ValueError as e:
        await message.answer(f"❌ Ошибка: {str(e)}\nПопробуйте еще раз:")

@booking_router.message(BookingStates.CHOOSE_CHECKOUT)
async def process_checkout(message: types.Message, state: FSMContext, postgres_db: PostgresDatabase):
    try:
        checkout_date = await validate_date(message.text)
        data = await state.get_data()
        
        if checkout_date <= data['checkin']:
            await message.answer("❌ Дата выезда должна быть позже даты заезда")
            return

        async with postgres_db.session_scope() as session:
            room_crud = RoomCRUD(session)
            available_rooms = await room_crud.get_available_rooms(
                data['checkin'], 
                checkout_date
            )
            
        if not available_rooms:
            await message.answer("😔 Нет доступных номеров на эти даты")
            await state.clear()
            return
            
        sent_message = await show_rooms_page(message, available_rooms, page=0)
        await state.update_data(
            checkout=checkout_date,
            available_rooms=available_rooms,
            rooms_message_id=sent_message.message_id,
            current_page=0
        )
        await state.set_state(BookingStates.SELECT_ROOM)
        
    except Exception as e:
        logging.error(f"Ошибка: {str(e)}", exc_info=True)
        await message.answer(f"❌ Ошибка: {str(e)}\nПопробуйте еще раз:")

async def show_rooms_page(message: types.Message, rooms: list, page: int) -> types.Message:
    PAGE_SIZE = 5
    total_pages = (len(rooms) + PAGE_SIZE - 1) // PAGE_SIZE
    page_rooms = rooms[page*PAGE_SIZE : (page+1)*PAGE_SIZE]
    
    builder = InlineKeyboardBuilder()
    for room in page_rooms:
        builder.button(
            text=f"№{room.number} ({room.type}) - {room.price}₽",
            callback_data=f"select_room_{room.id}"
        )
    
    pagination = InlineKeyboardBuilder()
    if page > 0:
        pagination.button(text="⬅️ Назад", callback_data=f"prev_page_{page}")
    if (page + 1) * PAGE_SIZE < len(rooms):
        pagination.button(text="➡️ Вперед", callback_data=f"next_page_{page}")
    
    builder.adjust(1, repeat=True)
    pagination.adjust(2)
    
    keyboard = InlineKeyboardBuilder()
    keyboard.attach(builder)
    keyboard.attach(pagination)
    
    return await message.answer(
        f"🏨 Доступные номера (Страница {page+1}/{total_pages}):\n\n" +
        "\n".join(f"• №{room.number} ({room.type}) - {room.price}₽/ночь" for room in page_rooms),
        reply_markup=keyboard.as_markup()
    )

@booking_router.callback_query(F.data.startswith("prev_page_"), F.data.startswith("next_page_"))
async def paginate_rooms(callback: types.CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        available_rooms = data.get("available_rooms", [])
        current_page = data.get("current_page", 0)
        
        if not available_rooms:
            await callback.answer("❌ Нет доступных номеров")
            return
        
        action, _, page = callback.data.partition("_page_")
        current_page = int(page)
        new_page = current_page - 1 if action == "prev" else current_page + 1
        
        PAGE_SIZE = 5
        total_pages = (len(available_rooms) + PAGE_SIZE - 1) // PAGE_SIZE
        
        if new_page < 0 or new_page >= total_pages:
            await callback.answer("❌ Нет доступных страниц")
            return
        
        page_rooms = available_rooms[new_page*PAGE_SIZE : (new_page+1)*PAGE_SIZE]
        
        builder = InlineKeyboardBuilder()
        for room in page_rooms:
            builder.button(
                text=f"№{room.number} ({room.type}) - {room.price}₽",
                callback_data=f"select_room_{room.id}"
            )
        
        pagination = InlineKeyboardBuilder()
        if new_page > 0:
            pagination.button(text="⬅️ Назад", callback_data=f"prev_page_{new_page}")
        if (new_page + 1) * PAGE_SIZE < len(available_rooms):
            pagination.button(text="➡️ Вперед", callback_data=f"next_page_{new_page}")
        
        builder.adjust(1, repeat=True)
        pagination.adjust(2)
        
        keyboard = InlineKeyboardBuilder()
        keyboard.attach(builder)
        keyboard.attach(pagination)
        
        await callback.message.edit_text(
            f"🏨 Доступные номера (Страница {new_page+1}/{total_pages}):\n\n" +
            "\n".join(f"• №{room.number} ({room.type}) - {room.price}₽/ночь" for room in page_rooms),
            reply_markup=keyboard.as_markup()
        )
        await state.update_data(current_page=new_page)
        await callback.answer()
        
    except Exception as e:
        logging.error(f"Ошибка пагинации: {str(e)}", exc_info=True)
        await callback.answer("❌ Ошибка переключения страниц")

@booking_router.callback_query(F.data.startswith("select_room_"))
async def select_room(callback: types.CallbackQuery, state: FSMContext, postgres_db: PostgresDatabase):
    try:
        room_id = int(callback.data.split("_")[-1])
        
        async with postgres_db.session_scope() as session:
            room_crud = RoomCRUD(session)
            room = await room_crud.get_room_by_id(room_id)
            
        if not room:
            await callback.answer("❌ Номер не найден")
            return
        
        await state.update_data(
            room_id=room.id,
            room_number=room.number,
            room_type=room.type,
            room_price=float(room.price)
        )
        
        data = await state.get_data()
        days = (data['checkout'] - data['checkin']).days
        total = days * data['room_price']
        
        markup = InlineKeyboardBuilder()
        markup.button(text="✅ Подтвердить", callback_data="confirm_booking")
        markup.button(text="❌ Отменить", callback_data="cancel_booking_process")
        markup.adjust(2)
        
        await callback.message.answer(
            f"🔎 Подтвердите бронирование:\n\n"
            f"📅 Заезд: {data['checkin'].strftime('%d.%m.%Y')}\n"
            f"📅 Выезд: {data['checkout'].strftime('%d.%m.%Y')}\n"
            f"🏠 Номер: №{room.number} ({room.type})\n"
            f"💵 Сумма: {total:.2f}₽",
            reply_markup=markup.as_markup()
        )
        await state.set_state(BookingStates.CONFIRM_BOOKING)
        
    except Exception as e:
        logging.error(f"Ошибка выбора номера: {str(e)}", exc_info=True)
        await callback.answer("❌ Ошибка выбора номера")

@booking_router.callback_query(F.data == "confirm_booking")
async def confirm_booking(callback: types.CallbackQuery, state: FSMContext):
    markup = InlineKeyboardBuilder()
    markup.button(text="💳 Оплатить сейчас", callback_data="fake_payment")
    markup.button(text="🔄 Изменить даты", callback_data="change_dates")
    markup.adjust(1)
    
    await callback.message.answer(
        "💸 Выберите действие:",
        reply_markup=markup.as_markup()
    )
    await state.set_state(BookingStates.PAYMENT)

@booking_router.callback_query(F.data == "fake_payment")
async def process_payment(callback: types.CallbackQuery, state: FSMContext, postgres_db: PostgresDatabase):

    data = await state.get_data()
        
    async with postgres_db.session_scope() as session:
        booking_crud = BookingCRUD(session)
        booking = await booking_crud.create_booking(
            user_id=callback.from_user.id,
            room_id=data['room_id'],
            check_in=data['checkin'],
            check_out=data['checkout'],
            total_price=(data['checkout'] - data['checkin']).days * data['room_price']
        )
            
        room_crud = RoomCRUD(session)
        await room_crud.update_room_status(
            room_id=data['room_id'],
            status=RoomStatusEnum.BOOKED
        )
            
        await session.commit()

    await callback.message.answer(
            "✅ Бронирование подтверждено!\n"
            f"🔖 Номер брони: {booking.id}\n"
            f"🏠 Номер: {data['room_number']}\n"
            f"📅 Даты: {data['checkin'].strftime('%d.%m')}-{data['checkout'].strftime('%d.%m')}\n"
            f"💵 Сумма: {booking.total_price:.2f}₽",
            reply_markup=main_keyboard()
    )
        
    await state.clear()

    # except Exception as e:
    #     logging.error(f"Критическая ошибка бронирования: {str(e)}", exc_info=True)
    #     await callback.answer("❌ Ошибка бронирования")
    #     await state.clear()

@booking_router.callback_query(F.data == "cancel_booking_process")
async def cancel_booking_process(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Бронирование отменено")
    await callback.message.answer(
        "Вы вернулись в главное меню:",
        reply_markup=main_keyboard()
    )
    await callback.answer()

@booking_router.message(F.text == "❌ Отменить бронь")
async def cancel_existing_booking_menu(message: types.Message, postgres_db: PostgresDatabase):
    try:
        async with postgres_db.session_scope() as session:
            booking_crud = BookingCRUD(session)
            bookings = await booking_crud.get_user_bookings(message.from_user.id)
            
        if not bookings:
            await message.answer("❌ У вас нет активных бронирований")
            return
            
        keyboard = InlineKeyboardBuilder()
        for booking in bookings:
            keyboard.button(
                text=f"Бронь #{booking.id} ({booking.check_in.strftime('%d.%m')}-{booking.check_out.strftime('%d.%m')})", 
                callback_data=f"cancel_booking_{booking.id}"
            )
        keyboard.adjust(1)
        
        await message.answer(
            "📋 Выберите бронирование для отмены:",
            reply_markup=keyboard.as_markup()
        )
        
    except Exception as e:
        logging.error(f"Ошибка: {str(e)}")
        await message.answer("❌ Ошибка получения данных")

@booking_router.callback_query(F.data.startswith("cancel_booking_"))
async def process_cancel_booking(callback: types.CallbackQuery, postgres_db: PostgresDatabase):
    try:
        booking_id = int(callback.data.split("_")[-1])
        
        async with postgres_db.session_scope() as session:
            booking_crud = BookingCRUD(session)
            await booking_crud.cancel_booking(booking_id)
            await session.commit()
            
        await callback.message.edit_text(
            "✅ Бронирование успешно отменено\n" 
            "💰 Средства будут возвращены в течение 3 рабочих дней"
        )
        await callback.answer()
        
    except Exception as e:
        logging.error(f"Ошибка отмены: {str(e)}")
        await callback.answer("❌ Ошибка отмены бронирования")