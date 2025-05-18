import logging

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from datetime import datetime, timedelta
from services.postgres_crud import BookingCRUD, RoomCRUD
from services.postgres_database import PostgresDatabase
from keyboards.user import main_keyboard
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from config.config import config

booking_router = Router()

class BookingStates(StatesGroup):
    CHOOSE_CHECKIN = State()
    CHOOSE_CHECKOUT = State()
    SELECT_ROOM = State()
    CONFIRM_BOOKING = State()
    PAYMENT = State()

async def date_keyboard():
    builder = ReplyKeyboardBuilder()
    today = datetime.today()
    for i in range(1, 31):
        date = today + timedelta(days=i)
        builder.button(text=date.strftime("%d.%m.%Y"))
    builder.adjust(4)
    return builder.as_markup(resize_keyboard=True)