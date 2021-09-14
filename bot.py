#!/usr/bin/python
# -*- coding: utf-8 -*-
from os import stat
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


async def get_event_type(event):
    pass


async def get_user_state_from_inline_commands(message):
    session = Session()
    print(message)
    customer = (
        session.query(Customer)
        .filter(Customer.id == message["message"]["chat"]["id"])
        .first()
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


async def get_user_state_from_text_commands(message):
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
            alert,
            reply_markup=default_keyboards[
                get_user_state_from_text_commands(message["chat"]["id"])
            ],
        )

    @staticmethod
    async def set_default_state(message):
        session = Session()
        customer = (
            session.query(Customer).filter(Customer.id == message["chat"]["id"]).first()
        )
        customer.current_state = ""


class OnboardingState:
    @staticmethod
    async def commands_handler(message):
        try:
            if message["id"]:
                command = message["data"]
        except KeyError as error:
            pass
        try:
            if message["message_id"]:
                command = message["text"]
        except KeyError as error:
            pass
        try:
            await OnboardingState_commands[command](message)
        except KeyError as error:
            await message.answer("Команда не найдена")

    @staticmethod
    async def send_onboarding_step(message):
        print(message, "тимур")
        session = Session()
        customer = (
            session.query(Customer).filter(Customer.id == message["from"]["id"]).first()
        )
        await bot.edit_message_text(
            onboarding_steps[customer.onboarding_page],
            customer.id,
            customer.last_sended_message_id,
        )
        if customer.onboarding_page == 1:
            await bot.edit_message_reply_markup(
                customer.id,
                customer.last_sended_message_id,
                reply_markup=first_onboarding_step_keyboard,
            )
        elif 1 <= customer.onboarding_page < 5:
            print("PIZDEC")
            await bot.edit_message_reply_markup(
                customer.id,
                customer.last_sended_message_id,
                reply_markup=next_prev_onboarding_keyboard,
            )
        elif customer.onboarding_page == 5:
            await bot.edit_message_reply_markup(
                customer.id, customer.last_sended_message_id
            )
            await OnboardingState.exit_onboarding_state(message)

    @staticmethod
    async def set_next_onboarding_step(message):
        session = Session()
        customer = (
            session.query(Customer).filter(Customer.id == message["from"]["id"]).first()
        )
        if customer.onboarding_page <= 5:
            customer.onboarding_page += 1
            session.commit()
            await OnboardingState.send_onboarding_step(message)

    @staticmethod
    async def set_prev_onboarding_step(message):
        session = Session()
        customer = (
            session.query(Customer).filter(Customer.id == message["from"]["id"]).first()
        )
        if customer.onboarding_page > 1:
            customer.onboarding_page -= 1
            session.commit()
            await OnboardingState.send_onboarding_step(message)

    @staticmethod
    async def exit_onboarding_state(message):
        print("ewe")
        session = Session()
        customer = (
            session.query(Customer).filter(Customer.id == message["from"]["id"]).first()
        )
        customer.state = "UndefinedKoala"
        customer.onboarding_page = 1
        session.commit()
        await bot.send_message(
            customer.id,
            "Вжух! И магическая клавиатура, о которой я говорил, открылась перед тобой только что!",
            reply_markup=user_main_menu_keyboard,
        )


class GameState:
    pass


class EducationState:
    pass


class UndefinedKoala(BaseState):
    @staticmethod
    async def commands_handler(message):
        try:
            if message["id"]:
                command = message["data"]
        except KeyError as error:
            pass
        try:
            if message["message_id"]:
                command = message["text"]
        except KeyError as error:
            pass
        try:
            await UndefinedKoala_commands[command](message)
        except KeyError as error:
            await message.answer("Команда не найдена")

    @staticmethod
    async def send_onboarding_request(message):
        await asyncio.sleep(1.5)
        last_message = await message.answer(
            "⚠️ Хочешь я тебе расскажу, из чего состоит бот и как им пользоваться?",
            reply_markup=onboarding_request_keyboard,
        )
        session = Session()
        customer = (
            session.query(Customer).filter(Customer.id == message["chat"]["id"]).first()
        )
        customer.last_sended_message_id = last_message["message_id"]
        session.commit()

    @staticmethod
    async def cancel_onboarding_request(message):
        pass

    @staticmethod
    async def accept_onboarding_request(message):
        print(15)
        session = Session()
        customer = (
            session.query(Customer)
            .filter(Customer.id == message["message"]["chat"]["id"])
            .first()
        )
        customer.current_state = "OnboardingState"
        session.commit()
        await OnboardingState.send_onboarding_step(message)

    @staticmethod
    async def start(message):
        await message.answer(
            "👋 Привет! \n\nЭто Tatrika — бот, с помощью которого ты сможешь изучать татарский язык, тратя всего 15 минут в день!\n\nПроходи мини-уроки, соревнуйся вместе с друзьями в играх, а если возникли вопросы, смело задавай их своему наставнику."
        )
        await asyncio.sleep(1.5)
        await UndefinedKoala.send_onboarding_request(message)

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
                    reply_markup=empty_keyboard,
                )
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
            "Хорошо, но если всё же захочешь поделиться номером телефона, это всегда можно будет сделать в разделе Настройки.",
            reply_markup=empty_keyboard,
        )
        await UndefinedKoala.send_onboarding_request(message)


class User(BaseState):
    @staticmethod
    async def commands_handler(message):
        try:
            if message["id"]:
                command = message["data"]
        except KeyError as error:
            pass
        try:
            if message["message_id"]:
                command = message["text"]
        except KeyError as error:
            pass
        try:
            print(command)
            await User_commands[command](message)
        except Exception as error:
            await message.answer(error)

    @staticmethod
    async def start(message):
        await message.answer(
            "👋 Привет! \n\nЭто Tatrika — бот, с помощью которого ты сможешь изучать татарский язык, тратя всего 15 минут в день!\n\nПроходи мини-уроки, соревнуйся вместе с друзьями в играх, а если возникли вопросы, смело задавай их своему наставнику."
        )


OnboardingState_commands = {
    "next_onboarding_step": OnboardingState.set_next_onboarding_step,
    "prev_onboarding_step": OnboardingState.set_prev_onboarding_step,
}


UndefinedKoala_commands = {
    "/start": UndefinedKoala.start,
    "accept_onboarding_request": UndefinedKoala.accept_onboarding_request,
    "cancel_onboarding_request": UndefinedKoala.cancel_onboarding_request,
}

User_commands = {
    "/start": User.start,
    "Изучать": 0,
    "Играть": 0,
    "Задать вопрос": 0,
    "Настройки": 0,
}

states = {
    "UndefinedKoala": UndefinedKoala,
    "EducationState": EducationState,
    "OnboardingState": OnboardingState,
    "User": User,
}


bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler()
async def text_commands_handler(message):
    user_state = await get_user_state_from_text_commands(message)
    await states[user_state].commands_handler(message)


@dp.callback_query_handler()
async def inline_commands_handler(message):
    user_state = await get_user_state_from_inline_commands(message)
    await states[user_state].commands_handler(message)


@dp.message_handler(content_types=["contact"])
async def get_contact(message):
    user_state = await get_user_state_from_text_commands(message)
    await states[user_state].auth_with_phone(message)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
