import sys
import pathlib
import aiosqlite
import pandas as pd
from aiogram import F
from aiogram import  Dispatcher, types
from aiogram.utils.keyboard import InlineKeyboardBuilder

script_dir = pathlib.Path(sys.argv[0]).parent
DB_NAME = script_dir / 'test_bot.db'
question_data = pd.read_csv("question_data.csv")
question_data['options'] = question_data['options'].apply(lambda x: x.split(","))
dp = Dispatcher()

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
    current_question_points = await get_test_points(callback.from_user.id)
    current_question_points += int(callback.data[-1])
    await update_test_index_points(callback.from_user.id, current_question_index, current_question_points)
    if current_question_index < len(question_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer(f"Это был последний вопрос. Тест завершен! Ваш результат - {current_question_points}.")

@dp.callback_query(F.data.startswith("right_"))
async def right_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    current_question_index = await get_test_index(callback.from_user.id)
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

async def get_test_index(user_id):
     async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT question_index FROM test_state WHERE user_id = (?)', (user_id, )) as cursor:
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0

async def get_test_points(user_id):
     async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT points FROM test_state WHERE user_id = (?)', (user_id, )) as cursor:
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0

async def update_test_index_points(user_id, index, points):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT OR REPLACE INTO test_state (user_id, question_index, points) VALUES (?, ?, ?)', (user_id, index, points))
        await db.commit()

async def create_table():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS test_state (user_id INTEGER PRIMARY KEY, question_index INTEGER, points INTEGER)''')
        await db.commit()