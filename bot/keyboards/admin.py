from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

def admin_panel_keyboard():
    return InlineKeyboardBuilder().add(
        types.InlineKeyboardButton(text="🏠 Номера", callback_data="rooms_management"),
        types.InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats"),
        types.InlineKeyboardButton(text="📝 Отзывы", callback_data="admin_reviews")
    ).adjust(2).as_markup()

def rooms_management_keyboard():
    return InlineKeyboardBuilder().add(
        types.InlineKeyboardButton(text="📋 Список номеров", callback_data="rooms_list"),
        types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_statuses"),
        types.InlineKeyboardButton(text="🔙 Назад", callback_data="admin_menu")
    ).adjust(1).as_markup()