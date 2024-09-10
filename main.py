import asyncio
import logging
import aiosqlite
from test import *
import pandas as pd
from aiogram import F
from aiogram import types
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

API_TOKEN = "7404804929:AAFuXD8pshvqK8JPKFRQY1yiXXDCSGWw3lQ"
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Тест"))
    await message.answer("Поехали! Нажмите 'Тест' для проверки своих знаний.", reply_markup=builder.as_markup(resize_keyboard=True))
    
@dp.message(F.text=="Тест")
async def cmd_test(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="В меню"))
    await message.answer(f"Давайте начнем тест!", reply_markup=builder.as_markup(resize_keyboard=True))
    await new_test(message)

@dp.message(F.text=="В меню")
async def cmd_menu(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Тест"))
    await message.answer("Нажмите 'Тест' для проверки своих знаний.", reply_markup=builder.as_markup(resize_keyboard=True))

"""#file test.py    
DB_NAME = 'test_bot.db'
question_data = pd.read_csv("question_data.csv")
question_data['options'] = question_data['options'].apply(lambda x: x.split(","))

def generate_options_keyboard(answer_options, right_answer):
    builder = InlineKeyboardBuilder()

    for option in answer_options:
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data= "right_" + option if option == right_answer else "wrong_" + option)
        )

    builder.adjust(2)
    return builder.as_markup()

async def check_last_question(callback: types.CallbackQuery):
    current_question_index = await get_test_index(callback.from_user.id)
    current_question_index += 1
    await update_test_index(callback.from_user.id, current_question_index)
    if current_question_index < len(question_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer("Это был последний вопрос. Тест завершен!")

@dp.callback_query(F.data.startswith("right_"))
async def right_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    await callback.message.answer(f"Ваш вариант отвера: {callback.data[6:]}, верен!")
    await check_last_question(callback)

@dp.callback_query(F.data.startswith("wrong_"))
async def wrong_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    current_question_index = await get_test_index(callback.from_user.id)
    correct_option = question_data['correct_option'][current_question_index]
    await callback.message.answer(f"Ваш вариант отвера: {callback.data[6:]}, не верен!")
    await callback.message.answer(f"Правильный ответ: {question_data['options'][current_question_index][correct_option]}")
    await check_last_question(callback)

async def get_question(message, user_id):
    current_question_index = await get_test_index(user_id)
    correct_index = question_data['correct_option'][current_question_index]
    opts = question_data['options'][current_question_index]
    kb = generate_options_keyboard(opts, opts[correct_index])
    await message.answer(f"{question_data['question'][current_question_index]}", reply_markup=kb)

async def new_test(message):
    user_id = message.from_user.id
    current_question_index = 0
    await update_test_index(user_id, current_question_index)
    await get_question(message, user_id)

async def get_test_index(user_id):
     async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT question_index FROM test_state WHERE user_id = (?)', (user_id, )) as cursor:
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0
            
async def update_test_index(user_id, index):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT OR REPLACE INTO test_state (user_id, question_index) VALUES (?, ?)', (user_id, index))
        await db.commit()

async def create_table():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS test_state (user_id INTEGER PRIMARY KEY, question_index INTEGER)''')
        await db.commit()
#file test.py"""

async def main():
    await dp.start_polling(bot)
    await create_table()

if __name__ == "__main__":
    asyncio.run(main()) 