from aiogram.utils.keyboard import ReplyKeyboardBuilder

def main_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="🛎 Бронирование")
    builder.button(text="🍽 Ресторан")
    builder.button(text="🍸 Бар")
    builder.button(text="📝 Отзыв")
    builder.button(text="📞 Контакты")
    builder.button(text="ℹ️ О отеле")
    builder.adjust(2, 2, 2)
    return builder.as_markup(resize_keyboard=True)