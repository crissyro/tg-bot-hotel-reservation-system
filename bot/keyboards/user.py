from aiogram.utils.keyboard import ReplyKeyboardBuilder

def main_keyboard():
    builder = ReplyKeyboardBuilder()
    buttons = [
        ("🛎 Бронирование",),
        ("💳 Оплатить бронь",),
        ("❌ Отменить бронь",),
        ("📝 Отзыв",),
        ("📞 Контакты",),
        ("ℹ️ О нас",)
    ]
    
    for text in buttons:
        builder.button(text=text[0])
    
    builder.adjust(2, 2, 2)
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Выберите действие..."
    )

def back_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="↩️ Главное меню")
    return builder.as_markup(resize_keyboard=True)
