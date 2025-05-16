import logging
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from services.mongo_database import MongoDatabase
from models.mongo_models import Review
from keyboards.user import main_keyboard

feedback_router = Router()

class FeedbackStates(StatesGroup):
    waiting_for_review = State()
    waiting_for_rating = State()

def back_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="↩️ Отмена")
    return builder.as_markup(resize_keyboard=True)

@feedback_router.message(F.text == "📝 Отзыв")
async def handle_feedback(message: types.Message, state: FSMContext):
    await state.set_state(FeedbackStates.waiting_for_review)
    await message.answer(
        "💬 Напишите ваш отзыв об отеле:",
        reply_markup=back_keyboard()
    )

@feedback_router.message(FeedbackStates.waiting_for_review, F.text == "↩️ Отмена")
async def cancel_feedback(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "❌ Создание отзыва отменено",
        reply_markup=main_keyboard()
    )

@feedback_router.message(FeedbackStates.waiting_for_review)
async def process_review(message: types.Message, state: FSMContext):
    await state.update_data(review_text=message.text)
    await state.set_state(FeedbackStates.waiting_for_rating)
    await message.answer(
        "⭐️ Введите оценку от 0 до 10:\n"
        "(0 - очень плохо, 10 - отлично)",
        reply_markup=back_keyboard()
    )

@feedback_router.message(FeedbackStates.waiting_for_rating, F.text == "↩️ Отмена")
async def cancel_rating(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "❌ Создание отзыва отменено",
        reply_markup=main_keyboard()
    )

# @feedback_router.message(FeedbackStates.waiting_for_rating)
# async def process_rating(message: types.Message, state: FSMContext, mongo_db: MongoDatabase):
#     try:
#         rating = int(message.text)
#         if 0 <= rating <= 10:
#             data = await state.get_data()
            
#             review = Review(
#                 user_id=message.from_user.id,
#                 user_name=message.from_user.full_name,
#                 text=data['review_text'],
#                 rating=rating
#             )
            
#             collection = mongo_db.get_reviews_collection()
#             result = await collection.insert_one(review.model_dump())
            
#             if result.acknowledged:
#                 await message.answer(
#                     "✅ Спасибо за ваш отзыв!",
#                     reply_markup=main_keyboard()
#                 )
#                 logging.info(f"Отзыв сохранен. ID: {result.inserted_id}")
#             else:
#                 await message.answer("❌ Ошибка при сохранении отзыва")
#                 logging.error("Не удалось сохранить отзыв")
            
#             await state.clear()
#         else:
#             await message.answer("⚠️ Оценка должна быть от 0 до 10. Попробуйте снова:")
#     except ValueError:
#         await message.answer("❌ Пожалуйста, введите число от 0 до 10:")
#     except Exception as e:
#         logging.error(f"Ошибка при сохранении отзыва: {str(e)}")
#         await message.answer("❌ Произошла ошибка при обработке вашего отзыва")
#         await state.clear()
        
@feedback_router.message(FeedbackStates.waiting_for_rating)
async def process_rating(message: types.Message, state: FSMContext, mongo_db: MongoDatabase):
    try:
        rating = int(message.text)
        if 0 <= rating <= 10:
            data = await state.get_data()
            
            review = Review(
                user_id=message.from_user.id,
                user_name=message.from_user.full_name,
                text=data['review_text'],
                rating=rating
            )
            
            collection = mongo_db.get_reviews_collection()
            result = await collection.insert_one(review.model_dump())
            
            if result.acknowledged:
                await message.answer("✅ Спасибо за отзыв!", reply_markup=main_keyboard())
            else:
                await message.answer("❌ Ошибка сохранения", reply_markup=main_keyboard())
            
            await state.clear()
        else:
            await message.answer("⚠️ Введите 0-10:")
    except Exception as e:
        logging.error(f"Ошибка: {str(e)}")
        await message.answer("❌ Ошибка обработки", reply_markup=main_keyboard())
        await state.clear()