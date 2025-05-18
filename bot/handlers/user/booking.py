import logging

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from datetime import datetime
from services.postgres_crud import BookingCRUD, RoomCRUD
from services.postgres_database import PostgresDatabase
from keyboards.user import main_keyboard, back_keyboard
from config.config import config

booking_router = Router()

class BookingStates(StatesGroup):
    CHOOSE_CHECKIN = State()
    CHOOSE_CHECKOUT = State()
    SELECT_ROOM = State()
    CONFIRM_BOOKING = State()
    PAYMENT = State()
