import logging
from aiogram import Router, types, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder
from models.postgres_models import RoomStatusEnum
from services.postgres_crud.room_crud import RoomCRUD
from services.postgres_database import PostgresDatabase
from keyboards.admin import rooms_management_keyboard, room_actions_keyboard, admin_panel_keyboard, status_selection_keyboard

admin_rooms_router = Router()

class RoomManagementStates(StatesGroup):
    EDITING_ROOM = State()

@admin_rooms_router.callback_query(F.data == "admin_menu")
async def admin_menu_handler(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "🛠 Административное меню:",
        reply_markup=admin_panel_keyboard()
    )

@admin_rooms_router.callback_query(F.data == "rooms_management")
async def handle_rooms_management(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "🏨 Управление номерами:",
        reply_markup=rooms_management_keyboard()
    )

@admin_rooms_router.callback_query(F.data == "admin_stats")
async def show_statistics(callback: types.CallbackQuery, postgres_db: PostgresDatabase):
    try:
        async with postgres_db.session_scope() as session:
            crud = RoomCRUD(session)
            stats = await crud.get_rooms_statistics()
            
            text = (
                    "📊 Статистика за последние 30 дней:\n\n"
                    f"💰 Общий доход: {stats['total_income']:.2f}₽\n"
                    f"📅 Всего бронирований: {stats['total_bookings']}\n"
                    f"🏨 Всего номеров: {stats['total_rooms']}\n"
                    f"✅ Свободно: {stats['available_rooms']}\n"
                    f"⛔ Занято: {stats['total_rooms'] - stats['available_rooms']}"
                )
            
            await callback.message.edit_text(
                text,
                reply_markup=InlineKeyboardBuilder()
                    .button(text="🔙 Назад", callback_data="admin_menu")
                    .as_markup()
            )
            
    except Exception as e:
        logging.error(f"Statistics error: {str(e)}")
        await callback.answer("❌ Ошибка загрузки статистики")

@admin_rooms_router.callback_query(F.data == "refresh_statuses")
async def refresh_room_statuses(callback: types.CallbackQuery, postgres_db: PostgresDatabase):
    try:
        async with postgres_db.session_scope() as session:
            crud = RoomCRUD(session)
            await crud.refresh_rooms_availability()
            await callback.answer("✅ Статусы номеров обновлены")
            await list_rooms(callback, postgres_db)
    except Exception as e:
        logging.error(f"Refresh error: {str(e)}")
        await callback.answer("❌ Ошибка обновления статусов")

@admin_rooms_router.callback_query(F.data == "rooms_list")
async def list_rooms(callback: types.CallbackQuery, postgres_db: PostgresDatabase):
    try:
        async with postgres_db.session_scope() as session:
            crud = RoomCRUD(session)
            rooms = await crud.get_all_rooms()
        
        if not rooms:
            await callback.answer("📭 Нет доступных номеров")
            return

        text = "🏨 Список всех номеров:\n\n"
        for idx, room in enumerate(rooms, 1):
            status = "✅" if room.status == RoomStatusEnum.AVAILABLE else "⛔"
            text += f"{idx}. {status} №{room.number} ({room.type}) - {room.price}₽\n"

        builder = InlineKeyboardBuilder()
        builder.button(text="🔙 Назад", callback_data="rooms_management")
        
        await callback.message.edit_text(
            text,
            reply_markup=builder.as_markup()
        )
        
    except Exception as e:
        logging.error(f"List rooms error: {str(e)}")
        await callback.answer("❌ Ошибка загрузки списка")

@admin_rooms_router.callback_query(F.data.startswith("change_status_"))
async def change_status_handler(callback: types.CallbackQuery):
    room_id = int(callback.data.split("_")[-1])
    await callback.message.edit_text(
        "Выберите новый статус:",
        reply_markup=status_selection_keyboard(room_id)
    )

@admin_rooms_router.callback_query(F.data.startswith("set_status_"))
async def set_status_handler(callback: types.CallbackQuery, postgres_db: PostgresDatabase):
    _, _, room_id, status = callback.data.split("_")
    
    async with postgres_db.session_scope() as session:
        crud = RoomCRUD(session)
        await crud.update_room_status(
            room_id=int(room_id),
            status=RoomStatusEnum(status)
        )
    
    await callback.answer(f"✅ Статус изменен на {status.capitalize()}")
    await room_detail(callback, postgres_db)


@admin_rooms_router.callback_query(F.data.startswith("room_detail_"))
async def room_detail(callback: types.CallbackQuery, postgres_db: PostgresDatabase):
    try:
        room_id = int(callback.data.split("_")[-1])
        
        async with postgres_db.session_scope() as session:
            crud = RoomCRUD(session)
            room = await crud.get_room_by_id(room_id)
        
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
        
    except Exception as e:
        logging.error(f"Room detail error: {str(e)}")
        await callback.answer("❌ Ошибка загрузки данных")

@admin_rooms_router.callback_query(F.data.startswith("toggle_room_"))
async def toggle_room_status(callback: types.CallbackQuery, postgres_db: PostgresDatabase):
    try:
        room_id = int(callback.data.split("_")[-1])
        
        async with postgres_db.session_scope() as session:
            crud = RoomCRUD(session)
            room = await crud.get_room_by_id(room_id)
            
            if not room:
                await callback.answer("❌ Номер не найден")
                return
                
            new_status = not room.is_available
            await crud.update_room_status(room.id, new_status)
            
        await callback.answer(f"✅ Статус изменен: {'Доступен' if new_status else 'Недоступен'}")
        await room_detail(callback, postgres_db)
        
    except Exception as e:
        logging.error(f"Toggle status error: {str(e)}")
        await callback.answer("❌ Ошибка изменения статуса")


@admin_rooms_router.callback_query(F.data.startswith("delete_room_"))
async def delete_room(callback: types.CallbackQuery, postgres_db: PostgresDatabase):
    try:
        room_id = int(callback.data.split("_")[-1])
        
        async with postgres_db.session_scope() as session:
            crud = RoomCRUD(session)
            await crud.delete_room(room_id)
            
        await callback.answer("✅ Номер успешно удален")
        await list_rooms(callback, postgres_db)
        
    except Exception as e:
        logging.error(f"Delete room error: {str(e)}")
        await callback.answer("❌ Ошибка удаления номера")