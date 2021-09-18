#!/usr/bin/python
# -*- coding: utf-8 -*-
from os import stat
from aiogram import Bot, types
from requests import check_compatibility
from variables import *
from models import *
from sqlalchemy.ext.declarative import declarative_base
from aiogram.dispatcher import Dispatcher
from config import TOKEN
from aiogram.utils import executor
from aiogram.types import reply_keyboard
from aiogram.types.message import Message
from random import choice
from json import *
from keyboards import *
import asyncio
import os
import aiohttp
import time
import datetime
from config import *
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


Session = sessionmaker()
Session.configure(bind=engine)


async def get_event_type(event):
    pass


async def get_user_state_from_inline_commands(message):
    session = Session()
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


class CardsGameState:
    @staticmethod
    async def commands_handler(message):
        try:
            if message["id"]:
                command = message["data"]
                if command.startswith("cards_game"): 
                    await CardsGameState.check_answer(message)
        except KeyError as error:
            pass
        try:
            if message["message_id"]:
                command = message["text"]
        except KeyError as error:
            pass
        try:
            await CardsGameState_commands[command](message)
        except KeyError as error:
            await message.answer(
                f"Команда {command} не найдена, введи /exit, чтобы вернуться на начальный экран."
            )

    @staticmethod
    async def check_answer(message): 
        pass


    @staticmethod
    async def start(message):
        session = Session()
        customer = (
            session.query(Customer).filter(Customer.id == message["chat"]["id"]).first()
        )
        await bot.send_message(
            customer.id,
            "Как играть?\n\nБот отправляет тебе карточку-картинку с изображением какого-либо предмета, а тебе нужно выбрать правильное название предмета на татарском языке.",
            reply_markup=cards_game_keyboard,
        )
        await CardsGameState.send_card(message, True)

    @staticmethod
    async def send_card(message, is_first):
        session = Session()
        customer = (
            session.query(Customer).filter(Customer.id == message["from"]["id"]).first()
        )
        with open("cards/cards.json", "r", errors="ignore", encoding="utf-8") as file:
            data = load(file)
        card = choice(data)
        answers = [
            InlineKeyboardButton(
                r_a := choice(all_answers), callback_data=f"cards_game_{r_a}"
            )
            for i in range(3)
        ] + [InlineKeyboardButton(card["correct_answer"], callback_data=f"cards_game_{card['correct_answer']}")]
        answers_keyboard = InlineKeyboardMarkup()
        count = 0
        for answer in answers:
            if count == 2:
                answers_keyboard.row()
                count = 0
            else:
                answers_keyboard.insert(answer)
        if is_first:
            await bot.send_photo(
                chat_id=customer.id,
                photo=open(card["image_source"], "rb"),
                reply_markup=answers_keyboard,
            )

        else: 
            await bot.edit_message_media(
                chat_id=customer.id,
                message_id=customer.last_sended_message_id,
                media=open(card["image_source"], "rb"),
            )
            await bot.edit_message_reply_markup(
                customer.id,
                customer.last_sended_message_id,
                reply_markup=answers_keyboard,
            )

    @staticmethod
    async def exit(message):
        pass


class LKState:
    @staticmethod
    async def start(message):
        session = Session()
        customer = (
            session.query(Customer).filter(Customer.id == message["chat"]["id"]).first()
        )
        if customer.phone_number:
            customer.current_state = "LKState"
            session.commit()
            await message.answer(
                "Перейди по ссылке [ссылка], авторизуйся и введи код, который придёт тебе в этом чате"
            )
        else:
            await UndefinedKoala.send_phone_request(message)


class MentoringState:
    @staticmethod
    async def commands_handler(message):
        await MentoringState.check_question(message)

    @staticmethod
    async def start(message):
        await message.answer(
            f"⚠ Напиши свой вопрос в чат, и наши наставники постараются как можно скорее ответить на твой вопрос!\n\nНе забудь, вопросы должны быть связаны с учебным материалом или играми, а также длина вопроса не должна быть больше {suitable_question_length} символов."
        )
        session = Session()
        customer = (
            session.query(Customer).filter(Customer.id == message["chat"]["id"]).first()
        )
        customer.current_state = "MentoringState"
        session.commit()

    @staticmethod
    async def check_question(message):
        if len(message.text) <= suitable_question_length:
            await message.answer(
                f"✅ Вопрос успешно задан! Как только на него ответит наставник, мы сразу же пришлём уведомление."
            )
            session = Session()
            question = Question(customer_id=message["chat"]["id"], text=message.text)
            customer = (
                session.query(Customer)
                .filter(Customer.id == message["chat"]["id"])
                .first()
            )
            customer.current_state = customer.default_state
            session.add(question)
            session.commit()

        else:
            await message.answer(
                f"⚠ Длина вопроса получилась больше, чем {suitable_question_length}. Сократи вопрос и напиши его снова."
            )


class BaseState:
    @staticmethod
    async def exit_to_main(message):
        session = Session()
        customer = (
            session.query(Customer).filter(Customer.id == message["chat"]["id"]).first()
        )
        customer.current_state = customer.default_state
        session.commit()
        await message.answer(
            "Ты вернулся на начальный экран.",
            reply_markup=keyboards[await get_user_state_from_text_commands(message)],
        )


class OnboardingState(BaseState):
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
            await message.answer(
                f"Команда {command} не найдена, введи /exit, чтобы вернуться на начальный экран."
            )

    @staticmethod
    async def send_onboarding_step(message):
        session = Session()
        customer = (
            session.query(Customer).filter(Customer.id == message["from"]["id"]).first()
        )
        if 1 <= customer.onboarding_page <= 4:
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
            else:
                await bot.edit_message_reply_markup(
                    customer.id,
                    customer.last_sended_message_id,
                    reply_markup=next_prev_onboarding_keyboard,
                )
        elif customer.onboarding_page == 5:
            await bot.delete_message(customer.id, customer.last_sended_message_id)
            await OnboardingState.exit_onboarding_state(message)

    @staticmethod
    async def set_next_onboarding_step(message):
        session = Session()
        customer = (
            session.query(Customer).filter(Customer.id == message["from"]["id"]).first()
        )
        if customer.onboarding_page <= 4:
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
        session = Session()
        customer = (
            session.query(Customer).filter(Customer.id == message["from"]["id"]).first()
        )
        customer.current_state = "UndefinedKoala"
        customer.onboarding_page = 1
        session.commit()
        await bot.send_message(
            customer.id,
            "✅ Отлично!\n\nМы рассказали тебе об всём, что знаем о боте, а если что-то пропустили — не беда! Всегда интереснее исследовать что-то самому, без посторонней помощи 😉",
            reply_markup=UndefinedKoala_keyboard,
        )


class EducationState:
    pass


class UndefinedKoala:
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
            await message.answer(
                f"Команда {command} не найдена, введи /exit, чтобы вернуться на начальный экран."
            )

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
    async def start_cards_game_state(message):
        session = Session()
        customer = (
            session.query(Customer).filter(Customer.id == message["chat"]["id"]).first()
        )
        customer.current_state = "CardsGameState"
        session.commit()
        await CardsGameState.start(message)

    @staticmethod
    async def cancel_onboarding_request(message):
        session = Session()
        customer = (
            session.query(Customer).filter(Customer.id == message["from"]["id"]).first()
        )
        await bot.delete_message(customer.id, customer.last_sended_message_id)
        await bot.send_message(
            message["from"]["id"],
            "Хорошо, но если у тебя возникнут вопросы по работе с ботом, можешь пройти обучение по команде /edu или задать вопрос своему наставнику.",
            reply_markup=UndefinedKoala_keyboard,
        )

    @staticmethod
    async def accept_onboarding_request(message):
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
                session.commit()
                await message.answer(
                    "✅ Теперь тебе доступны все возможности авторизованных пользователей.",
                    reply_markup=UndefinedKoala_keyboard,
                )
                await LKState.start(message)
        else:
            await message.answer(
                "Делишься номером ещё до того, как тебя попросили об этом???\n\nНу и прекрасно!"
            )

    @staticmethod
    async def send_phone_request(message):
        await message.answer(
            "Поделись номером телефона, чтобы получить доступ к личному кабинету на сайте.\n\nЗачем мне нужен личный кабинет?\n✳ Отслеживать собственный прогресс в изучении татарского языка.\n\n",
            reply_markup=phone_request_keyboard,
        )

    @staticmethod
    async def cancel_phone_request(message):
        await message.answer(
            "Хорошо, но если всё же захочешь поделиться номером телефона, это всегда можно будет сделать в разделе Настройки.",
            reply_markup=empty_keyboard,
        )
        await UndefinedKoala.send_onboarding_request(message)

    @staticmethod
    async def send_game_selection_request(message):
        await bot.send_message(
            message["from"]["id"],
            "Выбери игру из списка ниже:",
            reply_markup=games_keyboard,
        )


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


onboarding_steps = {
    1: "😉 Отлично!\n\nСейчас я расскажу, из чего состоит бот и как им пользоваться. Для навигации используй кнопки < и >.",
    2: "*[1/3]* Первым делом стоит изучать теорию, за каждый пройденный шаг теории ты получаешь очки, которые потом обмениваются на достижения и бонусы! 1 шаг = 1 очко.\n\nКроме того, после прохождения некоторых шагов ты получишь возможность решить задания, верно решенное задание = 5 очков.",
    3: "*[2/3]* Теория уже надоела? Тогда сыграй в игры в одиночку или вместе с друзьями.\n\nЧтобы пригласить друга в игру, напиши в чат с другом @tatrikabot, выбери игру и начинай играть!",
    4: "*[3/3]* А что делать, если у меня возник вопрос по учебным материалам или играм?\n\nСмело задавай их своему наставнику через кнопку Задать вопрос!",
}

OnboardingState_commands = {
    "next_onboarding_step": OnboardingState.set_next_onboarding_step,
    "prev_onboarding_step": OnboardingState.set_prev_onboarding_step,
    "/exit": BaseState.exit_to_main,
}


UndefinedKoala_commands = {
    "/start": UndefinedKoala.start,
    "accept_onboarding_request": UndefinedKoala.accept_onboarding_request,
    "cancel_onboarding_request": UndefinedKoala.cancel_onboarding_request,
    "Изучать": 0,
    "Играть": UndefinedKoala.send_game_selection_request,
    "Задать вопрос": MentoringState.start,
    "Личный кабинет": LKState.start,
    "/exit": BaseState.exit_to_main,
    "Карточки": UndefinedKoala.start_cards_game_state,
    "Слова": 0,
}

CardsGameState_commands = {
    "Выйти из игры": CardsGameState.exit,
    "Следующая карточка": CardsGameState.send_card,
    "/exit": BaseState.exit_to_main,
}


states = {
    "UndefinedKoala": UndefinedKoala,
    "EducationState": EducationState,
    "OnboardingState": OnboardingState,
    "MentoringState": MentoringState,
    "LKState": LKState,
    "CardsGameState": CardsGameState,
}


keyboards = {"UndefinedKoala": UndefinedKoala_keyboard}


suitable_question_length = 140


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
