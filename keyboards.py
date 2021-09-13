from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.sql.functions import user

phone_request_button = KeyboardButton('Поделиться номером', request_contact=True)
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


accept_onboarding_request_button = InlineKeyboardButton("Хочу", callback_data="accept")
dicline_onboarding_request_button = InlineKeyboardButton("Пропустить", callback_data="dicline")
onboarding_request_keyboard = InlineKeyboardMarkup()
onboarding_request_keyboard.add(accept_onboarding_request_button, dicline_onboarding_request_button)






