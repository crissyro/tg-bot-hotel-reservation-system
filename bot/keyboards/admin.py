from aiogram.utils.keyboard import InlineKeyboardBuilder

def admin_panel_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Управление номерами", callback_data="admin_rooms")
    builder.button(text="Управление меню", callback_data="admin_menu")
    builder.button(text="Просмотр отзывов", callback_data="admin_reviews")
    builder.button(text="Статистика", callback_data="admin_stats")
    builder.adjust(1)
    return builder.as_markup()