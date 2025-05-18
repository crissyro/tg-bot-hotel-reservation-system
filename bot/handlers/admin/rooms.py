import logging
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.postgres_crud.room_crud import RoomCRUD
from services.postgres_database import PostgresDatabase
from keyboards.admin import room_actions_keyboard, rooms_management_keyboard

admin_rooms_router = Router()

class RoomManagementStates(StatesGroup):
    ADDING_ROOM = State()
    EDITING_ROOM = State()

@admin_rooms_router.callback_query(F.data == "rooms_management")
async def handle_rooms_management(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "🏨 Управление номерами:",
        reply_markup=rooms_management_keyboard()
    )

@admin_rooms_router.callback_query(F.data.startswith("toggle_room_"))
async def toggle_room_status(callback: types.CallbackQuery, 
                            postgres_db: PostgresDatabase):
    room_id = int(callback.data.split("_")[-1])
    
    async with postgres_db.session_scope() as session:
        room_crud = RoomCRUD(session)
        room = await room_crud.get_room(room_id)
        
        if not room:
            await callback.answer("❌ Номер не найден")
            return
            
        new_status = not room.is_available
        await room_crud.update_room_status(room.id, new_status)
        
    await callback.answer(f"✅ Статус изменен: {'Доступен' if new_status else 'Недоступен'}")
    await list_rooms(callback, postgres_db)

@admin_rooms_router.callback_query(F.data == "rooms_list")
async def list_rooms(callback: types.CallbackQuery, 
                   postgres_db: PostgresDatabase):
    try:
        async with postgres_db.session_scope() as session:
            room_crud = RoomCRUD(session)
            rooms = await room_crud.get_all_rooms()
        
        if not rooms:
            await callback.answer("📭 Нет доступных номеров")
            return

        text = "🏨 Список всех номеров:\n\n"
        for idx, room in enumerate(rooms, 1):
            text += f"{idx}. №{room.number} ({room.type}) - {room.price}₽ [{'✅' if room.is_available else '⛔'}]\n"

        builder = InlineKeyboardBuilder()
        builder.button(text="🔙 Назад", callback_data="admin_menu")
        
        await callback.message.edit_text(
            text,
            reply_markup=builder.as_markup()
        )
        
    except Exception as e:
        logging.error(f"List rooms error: {str(e)}")
        await callback.answer("❌ Ошибка загрузки списка")

@admin_rooms_router.callback_query(F.data.startswith("room_detail_"))
async def room_detail(callback: types.CallbackQuery, postgres_db: PostgresDatabase):
    room_id = int(callback.data.split("_")[-1])
    
    async with postgres_db.session_scope() as session:
        room_crud = RoomCRUD(session)
        room = await room_crud.get_room(room_id)
    
    if not room:
        await callback.answer("❌ Номер не найден")
        return
    
    text = (
        f"🏠 Номер №{room.number}\n"
        f"🔖 Тип: {room.type}\n"
        f"💰 Цена: {room.price}₽/ночь\n"
        f"📝 Описание: {room.description}\n"
        f"Статус: {'Доступен' if room.is_available else 'Недоступен'}"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=room_actions_keyboard(room.id)
    )

@admin_rooms_router.message(RoomManagementStates.ADDING_ROOM)
async def add_room_process(message: types.Message, state: FSMContext, postgres_db: PostgresDatabase):
    try:
        parts = message.text.split("|")
        if len(parts) < 4:
            raise ValueError
            
        number = parts[0].strip()
        room_type = parts[1].strip().lower()
        price = float(parts[2].strip())
        description = parts[3].strip()
        
        async with postgres_db.session_scope() as session:
            room_crud = RoomCRUD(session)
            await room_crud.create_room(number, room_type, price, description)
            
        await message.answer("✅ Номер успешно добавлен")
        await state.clear()
        
    except Exception:
        await message.answer("❌ Ошибка формата данных. Попробуйте еще раз:")
        