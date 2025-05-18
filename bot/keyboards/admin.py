from aiogram.utils.keyboard import InlineKeyboardBuilder

def admin_panel_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🏠 Номера", callback_data="admin_rooms")
    builder.button(text="🍽 Меню", callback_data="admin_food_menu")
    builder.button(text="📊 Статистика", callback_data="admin_stats")
    builder.button(text="📨 Рассылка", callback_data="admin_broadcast")
    builder.button(text="📝 Отзывы", callback_data="admin_reviews")
    builder.adjust(2, 2, 1)
    return builder.as_markup()

def rooms_management_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="📋 Список номеров", callback_data="rooms_list")
    builder.button(text="🔄 Обновить статусы", callback_data="refresh_rooms")
    builder.button(text="🔙 Назад", callback_data="admin_menu")
    builder.adjust(1)
    return builder.as_markup()

def room_actions_keyboard(room_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(text="🔄 Изменить статус", callback_data=f"toggle_room_{room_id}")
    builder.button(text="✏️ Редактировать", callback_data=f"edit_room_{room_id}")
    builder.button(text="🗑 Удалить", callback_data=f"delete_room_{room_id}")
    builder.button(text="🔙 Назад", callback_data="rooms_list")
    builder.adjust(1)
    return builder.as_markup()