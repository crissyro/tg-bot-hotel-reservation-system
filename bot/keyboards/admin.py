from aiogram.utils.keyboard import InlineKeyboardBuilder

from models.postgres_models import RoomStatusEnum

def admin_panel_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🏠 Номера", callback_data="rooms_management")
    builder.button(text="📊 Статистика", callback_data="admin_stats")
    builder.button(text="📝 Отзывы", callback_data="admin_reviews")
    builder.adjust(2)
    return builder.as_markup()

def rooms_management_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="📋 Список номеров", callback_data="rooms_list")
    builder.button(text="🔄 Обновить статусы", callback_data="refresh_statuses")
    builder.button(text="➕ Добавить номер", callback_data="add_room")
    builder.button(text="🔙 Назад", callback_data="admin_menu")
    builder.adjust(1, 2, 1)
    return builder.as_markup()

def room_actions_keyboard(room_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(text="🔄 Изменить статус", callback_data=f"change_status_{room_id}")
    builder.button(text="✏️ Редактировать", callback_data=f"edit_room_{room_id}")
    builder.button(text="🗑 Удалить", callback_data=f"delete_room_{room_id}")
    builder.button(text="🔙 Назад", callback_data="rooms_list")
    builder.adjust(1, 2, 1)
    return builder.as_markup()

def status_selection_keyboard(room_id: int):
    builder = InlineKeyboardBuilder()
    for status in RoomStatusEnum:
        builder.button(
            text=status.value.capitalize(),
            callback_data=f"set_status_{room_id}_{status.value}"
        )
    builder.button(text="🔙 Назад", callback_data=f"room_detail_{room_id}")
    builder.adjust(1)
    return builder.as_markup()