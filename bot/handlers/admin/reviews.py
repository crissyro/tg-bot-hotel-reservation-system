import logging
from aiogram import Router, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.mongo_database import MongoDatabase
from config.config import config

reviews_router = Router()

PAGE_SIZE = 5  

@reviews_router.callback_query(F.data == "admin_reviews")
async def show_reviews(callback: types.CallbackQuery, mongo_db: MongoDatabase):
    try:
        if callback.from_user.id not in config.ADMINS:
            await callback.answer("⛔ Доступ запрещен!")
            return

        collection = mongo_db.get_reviews_collection()
        all_reviews = await collection.find().sort("created_at", -1).to_list(None)
        
        if not all_reviews:
            await callback.message.edit_text("📭 Нет отзывов для просмотра")
            return

        text = format_reviews_page(all_reviews, page=0)
        markup = build_reviews_keyboard(len(all_reviews), current_page=0)
        
        await callback.message.edit_text(
            text,
            reply_markup=markup,
            parse_mode="HTML"
        )
        
    except Exception as e:
        logging.error(f"Ошибка при получении отзывов: {str(e)}")
        await callback.answer("❌ Ошибка загрузки отзывов")

def format_reviews_page(reviews: list, page: int) -> str:
    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    page_reviews = reviews[start:end]
    
    text = f"📃 <b>Отзывы (страница {page + 1})</b>\n\n"
    for review in page_reviews:
        text += (
            f"👤 {review.get('user_name', 'Аноним')}\n"
            f"⭐ Оценка: {review['rating']}/10\n"
            f"📅 {review['created_at'].strftime('%d.%m.%Y %H:%M')}\n"
            f"📝 {review['text']}\n"
            f"{'-'*30}\n"
        )
    return text

def build_reviews_keyboard(total: int, current_page: int) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    if current_page > 0:
        builder.button(text="⬅️ Назад", callback_data=f"reviews_page_{current_page - 1}")
    
    if (current_page + 1) * PAGE_SIZE < total:
        builder.button(text="Вперед ➡️", callback_data=f"reviews_page_{current_page + 1}")

    builder.adjust(2)
    return builder.as_markup()

@reviews_router.callback_query(F.data.startswith("reviews_page_"))
async def paginate_reviews(callback: types.CallbackQuery, mongo_db: MongoDatabase):
    page = int(callback.data.split("_")[-1])
    collection = mongo_db.get_reviews_collection()
    all_reviews = await collection.find().sort("created_at", -1).to_list(None)
    
    if not all_reviews:
        await callback.answer("📭 Отзывов больше нет")
        return
    
    text = format_reviews_page(all_reviews, page)
    markup = build_reviews_keyboard(len(all_reviews), page)
    
    await callback.message.edit_text(
        text,
        reply_markup=markup,
        parse_mode="HTML"
    )
    await callback.answer()