from aiogram.types import (
    ReplyKeyboardRemove,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from sqlalchemy.sql.functions import user

phone_request_button = KeyboardButton("Поделиться номером", request_contact=True)
cancel_phone_request_button = KeyboardButton("Не хочу")
phone_request_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
phone_request_keyboard.add(phone_request_button, cancel_phone_request_button)


user_main_menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
start_education_state_button = KeyboardButton("Изучать")
start_game_state_button = KeyboardButton("Играть")
start_mentoring_state_button = KeyboardButton("Задать вопрос")
user_main_menu_keyboard.add(start_education_state_button)
user_main_menu_keyboard.row()
user_main_menu_keyboard.add(start_game_state_button)
user_main_menu_keyboard.row()
user_main_menu_keyboard.add(start_mentoring_state_button)


accept_onboarding_request_button = InlineKeyboardButton(
    "Хочу", callback_data="accept_onboarding_request"
)
dicline_onboarding_request_button = InlineKeyboardButton(
    "Пропустить", callback_data="cancel_onboarding_request"
)
onboarding_request_keyboard = InlineKeyboardMarkup()
onboarding_request_keyboard.add(
    accept_onboarding_request_button, dicline_onboarding_request_button
)

first_onboarding_step_keyboard = InlineKeyboardMarkup()
first_onboarding_step_button = InlineKeyboardButton(
    ">", callback_data="next_onboarding_step"
)
first_onboarding_step_keyboard.add(first_onboarding_step_button)

next_onboarding_step_button = InlineKeyboardButton(
    "<", callback_data="prev_onboarding_step"
)
prev_onboarding_step_button = InlineKeyboardButton(
    ">", callback_data="next_onboarding_step"
)
next_prev_onboarding_keyboard = InlineKeyboardMarkup()
next_prev_onboarding_keyboard.add(
    next_onboarding_step_button, prev_onboarding_step_button
)

empty_keyboard = ReplyKeyboardRemove()
