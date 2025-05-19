import logging
from aiogram import Router, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from models.postgres_models import RoomStatusEnum
from services.postgres_crud.room_crud import RoomCRUD
from services.postgres_database import PostgresDatabase
from keyboards.admin import (
    admin_panel_keyboard,
    rooms_management_keyboard
)

admin_rooms_router = Router()

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
        logging.error(f"Ошибка статистики: {str(e)}")
        await callback.answer("❌ Ошибка загрузки статистики")

@admin_rooms_router.callback_query(F.data == "rooms_list")
async def list_rooms(callback: types.CallbackQuery, postgres_db: PostgresDatabase):
    try:
        async with postgres_db.session_scope() as session:
            crud = RoomCRUD(session)
            await crud.refresh_rooms_availability()  
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