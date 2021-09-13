#!/usr/bin/python
# -*- coding: utf-8 -*-
from aiogram import Bot, types
from variables import *
from models import *
from sqlalchemy.ext.declarative import declarative_base
from aiogram.dispatcher import Dispatcher
from config import TOKEN
from aiogram.utils import executor
from aiogram.types import reply_keyboard
from aiogram.types.message import Message
from random import choice
from keyboards import *
import asyncio
import aiohttp
import time
import datetime
from config import *
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


Session = sessionmaker()
engine = create_engine("sqlite:///prodb.db")
Session.configure(bind=engine)

default_keyboards = {
    "User": user_main_menu_keyboard,
    "UndefinedKoala": phone_request_keyboard,
}


async def get_user_state(message):
    session = Session()
    print(message)
    customer = (
        session.query(Customer).filter(Customer.id == message["chat"]["id"]).first()
    )
    if customer:
        return customer.current_state
    else:
        customer = Customer(
            id=message["from"]["id"],
            username=message["from"]["username"],
            current_state="UndefinedKoala",
        )
        session.add(customer)
        session.commit()
        return "UndefinedKoala"


class BaseState:
    @staticmethod
    async def send_default_keyboard(alert, message=None):
        message.answer(
            alert, reply_markup=default_keyboards[get_user_state(message["chat"]["id"])]
        )

    @staticmethod
    async def set_default_state(message):
        session = Session()
        customer = (
            session.query(Customer).filter(Customer.id == message["chat"]["id"]).first()
        )
        customer.current_state = ""


class GameState:
    pass


class EducationState:
    pass


class UndefinedKoala:
    @staticmethod
    async def commands_handler(message):
        try:
            await UndefinedKoala_commands[message.text](message)
        except KeyError as error:
            await message.answer("Команда не найдена")

    @staticmethod
    async def start(message):
        await message.answer(
            "👋 Привет! \n\nЭто Tatrika — бот, с помощью которого ты сможешь изучать татарский язык, тратя всего 15 минут в день!\n\nПроходи мини-уроки, соревнуйся вместе с друзьями в играх, а если возникли вопросы, смело задавай их своему наставнику."
        )
        await asyncio.sleep(1.5)
        await UndefinedKoala.send_phone_request_message(message)

    @staticmethod
    async def auth_with_phone(message):
        session = Session()
        customer = (
            session.query(Customer).filter(Customer.id == message["chat"]["id"]).first()
        )
        if customer:
            if customer.phone_number:
                await message.answer(
                    "Ты уже делился с нами номером телефона, тебе доступны все возможности авторизованных пользователей 😜"
                )
            else:
                customer.phone_number = message.contact.phone_number
                customer.current_state = "User"
                session.commit()
                await message.answer(
                    "Ура! 🎊 Теперь тебе доступны все возможности авторизованных пользователей.",
                    reply_markup=user_main_menu_keyboard,
                )
                await User.send_onboarding_message_request(message)
        else:
            await message.answer(
                "Делишься номером ещё до того, как тебя попросили об этом???\n\nНу и прекрасно!"
            )

    @staticmethod
    async def send_phone_request_message(message):
        await message.answer(
            "Поделись номером телефона, чтобы получить доступ к личному кабинету на сайте.\n\nЗачем мне нужен личный кабинет?\n✳ Отслеживать собственный прогресс в изучении татарского языка.\n\nЕсли не хочешь, этот шаг можно пропустить.",
            reply_markup=phone_request_keyboard,
        )

    @staticmethod
    async def cancel_phone_request(message):
        await message.answer(
            "Хорошо, но если всё же захочешь поделиться номером телефона, у тебя будет такая возможность.",
            reply_markup=user_main_menu_keyboard,
        )
        await UndefinedKoala.send_onboarding_message_request(message)

    @staticmethod
    async def send_onboarding_message_request(message): 
        await message.answer("Хочешь я тебе расскажу, из чего состоит бот и как им пользоваться?", reply_markup=onboarding_request_keyboard)


class OnboardingState: 
    @staticmethod
    async def first_step(message): 
        pass


class User(UndefinedKoala):
    @staticmethod
    async def commands_handler(message):
        try:
            await User_commands[message.text](message)
        except KeyError as error:
            await message.answer("Команда не найдена")

    @staticmethod
    async def start(message): 
        await message.answer(
            "👋 Привет! \n\nЭто Tatrika — бот, с помощью которого ты сможешь изучать татарский язык, тратя всего 15 минут в день!\n\nПроходи мини-уроки, соревнуйся вместе с друзьями в играх, а если возникли вопросы, смело задавай их своему наставнику."
        )

    @staticmethod
    async def send_onboarding_message_request(message): 
        await message.answer("Хочешь я тебе расскажу, из чего состоит бот и как им пользоваться?", reply_markup=onboarding_request_keyboard)


UndefinedKoala_commands = {
    "/start": UndefinedKoala.start,
    "Не хочу": UndefinedKoala.cancel_phone_request,
}

User_commands = {}

states = {
    "UndefinedKoala": UndefinedKoala,
    "EducationState": EducationState,
    "User": User,
}


bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler()
async def commands_handler(message):
    user_state = await get_user_state(message)
    print(user_state, 11010)
    await states[user_state].commands_handler(message)


@dp.message_handler(content_types=["contact"])
async def get_contact(message):
    user_state = await get_user_state(message)
    await states[user_state].auth_with_phone(message)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
