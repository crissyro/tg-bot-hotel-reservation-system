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