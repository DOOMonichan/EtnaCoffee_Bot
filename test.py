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
            callback_data= "right_" + option + "_answer" if option == right_answer else "wrong_" + option + "_answer")
        )

    builder.adjust(2)
    return builder.as_markup()

@dp.callback_query(F.data.endswith("_answer"))
async def answer_handler(callback: types.CallbackQuery) -> None:
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    current_question_index = await get_test_index(callback.from_user.id)
    current_user_score = await get_test_points(callback.from_user.id)
    
    answer = callback.data.replace("_answer", "")
    if answer.startswith("right_"):
        current_user_score += 1
        answer = answer.replace("right_", "")

        await callback.message.answer(f"Ваш вариант ответа: {answer}\nВерен!")
    else:
        answer = answer.replace("wrong_", "")
        correct_option = question_data['correct_option'][current_question_index]
        await callback.message.answer(f"Ваш ответ: {answer}. \nНеверен! \nПравильный ответ: {question_data['options'][current_question_index][correct_option]}")

    current_question_index += 1
    await update_test_index_points(callback.from_user.id, current_question_index, current_user_score)

    if current_question_index < len(question_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        end_message = await end_message_points(callback.from_user.id)
        await callback.message.answer(f"Это был последний вопрос. Тест завершен! \nВы набрали {end_message}.")

async def end_message_points(user_id):
    end_message = str(await get_test_points(user_id))
    if end_message == "1":
        end_message += " очко"
    elif end_message in ("2", "3", "4"):
        end_message += " очка"
    else:
        end_message += " очков"
    return end_message

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
            
async def rec_new_user(user_id, username, index, points):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT OR REPLACE INTO test_state (user_id, username, question_index, points) VALUES (?, ?, ?, ?)', (user_id, username, index, points))
        await db.commit()

async def get_username(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT username FROM test_state WHERE user_id = (?)', (user_id, )) as cursor:
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return None
            
async def update_test_index_points(user_id, index, points):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('UPDATE test_state SET (question_index, points) = (?, ?) WHERE user_id = ?', (index, points, user_id))
        await db.commit()

async def create_table():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS test_state (user_id INTEGER PRIMARY KEY, username TEXT NOT NULL, question_index INTEGER, points INTEGER)''')
        await db.commit()