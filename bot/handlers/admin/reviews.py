import logging
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.mongo_database import MongoDatabase
from models.mongo_models import Review
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
    for _, review in enumerate(page_reviews, start=1):
        text += (
            f"👤 <i>Пользователь:</i> {review.get('user_name', 'Аноним')}\n"
            f"⭐ <i>Оценка:</i> {review['rating']}/10\n"
            f"📅 <i>Дата:</i> {review['created_at'].strftime('%d.%m.%Y %H:%M')}\n"
            f"📝 <i>Отзыв:</i>\n{review['text']}\n"
            f"{'-'*30}\n"
        )
    return text

def build_reviews_keyboard(total: int, current_page: int) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    if current_page > 0:
        builder.button(text="⬅️ Назад", callback_data=f"reviews_page_{current_page - 1}")
    if (current_page + 1) * PAGE_SIZE < total:
        builder.button(text="Вперед ➡️", callback_data=f"reviews_page_{current_page + 1}")
    
    builder.button(text="✅ Одобрить все", callback_data="approve_all_reviews")
    builder.button(text="🗑 Удалить все", callback_data="delete_all_reviews")
    builder.button(text="🔙 Назад", callback_data="admin_panel")
    
    builder.adjust(2, 2, 1)
    
    return builder.as_markup()

@reviews_router.callback_query(F.data.startswith("reviews_page_"))
async def paginate_reviews(callback: types.CallbackQuery, mongo_db: MongoDatabase):
    page = int(callback.data.split("_")[-1])
    collection = mongo_db.get_reviews_collection()
    all_reviews = await collection.find().sort("created_at", -1).to_list(None)
    
    text = format_reviews_page(all_reviews, page)
    markup = build_reviews_keyboard(len(all_reviews), page)
    
    await callback.message.edit_text(
        text,
        reply_markup=markup,
        parse_mode="HTML"
    )
    
    await callback.answer()
    
@reviews_router.callback_query(F.data == "approve_all_reviews")
async def approve_all_reviews(callback: types.CallbackQuery, mongo_db: MongoDatabase):
    try:
        if callback.from_user.id not in config.ADMINS:
            await callback.answer("⛔ Доступ запрещен!")
            return
        
        builder = InlineKeyboardBuilder()
        builder.button(text="✅ Подтвердить", callback_data="confirm_approve_all")
        builder.button(text="❌ Отмена", callback_data="admin_reviews")
        builder.adjust(2)
        
        await callback.message.edit_text(
            "Вы уверены, что хотите одобрить ВСЕ отзывы?",
            reply_markup=builder.as_markup()
        )
        
    except Exception as e:
        logging.error(f"Ошибка одобрения: {str(e)}")
        await callback.answer("❌ Ошибка операции")

@reviews_router.callback_query(F.data == "confirm_approve_all")
async def confirm_approve_all(callback: types.CallbackQuery, mongo_db: MongoDatabase):
    try:
        collection = mongo_db.get_reviews_collection()
        result = await collection.update_many(
            {},
            {"$set": {"is_approved": True}}
        )
        
        await callback.answer(f"✅ Одобрено отзывов: {result.modified_count}")
        await show_reviews(callback, mongo_db) 
        
    except Exception as e:
        logging.error(f"Ошибка подтверждения: {str(e)}")
        await callback.answer("❌ Ошибка одобрения")

@reviews_router.callback_query(F.data == "delete_all_reviews")
async def delete_all_reviews(callback: types.CallbackQuery, mongo_db: MongoDatabase):
    try:
        if callback.from_user.id not in config.ADMINS:
            await callback.answer("⛔ Доступ запрещен!")
            return

        builder = InlineKeyboardBuilder()
        builder.button(text="🔥 Удалить", callback_data="confirm_delete_all")
        builder.button(text="❌ Отмена", callback_data="admin_reviews")
        builder.adjust(2)
        
        await callback.message.edit_text(
            "❌ Вы уверены, что хотите УДАЛИТЬ ВСЕ отзывы?",
            reply_markup=builder.as_markup()
        )
        
    except Exception as e:
        logging.error(f"Ошибка удаления: {str(e)}")
        await callback.answer("❌ Ошибка операции")

@reviews_router.callback_query(F.data == "confirm_delete_all")
async def confirm_delete_all(callback: types.CallbackQuery, mongo_db: MongoDatabase):
    try:
        collection = mongo_db.get_reviews_collection()
        result = await collection.delete_many({})
        
        await callback.answer(f"🗑 Удалено отзывов: {result.deleted_count}")
        await show_reviews(callback, mongo_db) 
        
    except Exception as e:
        logging.error(f"Ошибка удаления: {str(e)}")
        await callback.answer("❌ Ошибка удаления")

@reviews_router.callback_query(F.data == "admin_panel")
async def back_to_admin_panel(callback: types.CallbackQuery):
    from .admin_panel import show_admin_panel  
    await show_admin_panel(callback.message)
    await callback.answer()