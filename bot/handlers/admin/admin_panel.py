import logging
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config.config import config

async def show_admin_panel(message: types.Message):
    try:
        if message.from_user.id not in config.ADMINS:
            await message.answer("⛔ Доступ запрещен!")
            return

        builder = InlineKeyboardBuilder()
        builder.button(text="🏠 Номера", callback_data="admin_rooms")
        builder.button(text="🍽 Меню", callback_data="admin_menu")
        builder.button(text="📊 Статистика", callback_data="admin_stats")
        builder.button(text="📨 Рассылка", callback_data="admin_broadcast")
        builder.button(text="📝 Отзывы", callback_data="admin_reviews")
        builder.adjust(2, 2, 1)

        if message.text == "Админ-панель":
            await message.edit_text(
                "⚙️ Панель администратора:",
                reply_markup=builder.as_markup()
            )
        else:
            await message.answer(
                "⚙️ Панель администратора:",
                reply_markup=builder.as_markup()
            )

    except Exception as e:
        logging.error(f"Ошибка отображения админ-панели: {str(e)}")
        await message.answer("❌ Ошибка загрузки панели")