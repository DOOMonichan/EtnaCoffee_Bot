import asyncio
import logging
import aiosqlite
from aiogram import F
from aiogram import types
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
logging.basicConfig(level=logging.INFO)

API_TOKEN = "7404804929:AAFuXD8pshvqK8JPKFRQY1yiXXDCSGWw3lQ"
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

question_data =[
    {'question': 'Какой из перечислиных видов кофе более крепкий?',
        'options': ['Арабика', 'Либерика', 'Робуста', 'Эксцельза'],
        'correct_option': 2
    },
    {
        'question': 'Какая высота произростания Арабики?',
        'options': ['до 900м', 'от 900м', 'от 1200м', 'от 1500м'],
        'correct_option': 1
    },]
@dp.message(F.text=="Начать")
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать"))
    await message.answer("Поехали! Введите /test для проверки своих знаний.", reply_markup=builder.as_markup(resize_keyboard=True))

@dp.message(Command("test"))
async def cmd_test(message: types.Message):
    await message.answer(f"Давайте начнем тест!")
    await new_test(message)

async def new_test(message):
    user_id = message.from_user.id
    current_question_index = 0
    await update_test_index(user_id, current_question_index)
    await get_question(message, user_id)

async def get_question(message, user_id):
    current_question_index = await get_test_index(user_id)
    correct_index = question_data[current_question_index]['correct_option']
    opts = question_data[current_question_index]['options']
    kb = generate_options_keyboard(opts, opts[correct_index])
    await message.answer(f"{question_data[current_question_index]['question']}", reply_markup=kb)

def generate_options_keyboard(answer_options, right_answer):
    builder = InlineKeyboardBuilder()

    for option in answer_options:
        builder.add(types.InlineKeyboardButton(text=option,
            callback_data="right_answer" if option == right_answer else "wrong_answer")
        )

    builder.adjust(1)
    return builder.as_markup()

async def create_table():
    async with aiosqlite.connect('EtnaCoffee_bot.db') as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS test_state (user_id INTEGER PRIMARY KEY, question_index INTEGER)''')
        await db.commit()

async def update_test_index(user_id, index):
    async with aiosqlite.connect(question_data) as db:
        await db.execute('INSERT OR REPLACE INTO test_state (user_id, question_index) VALUES (?, ?)', (user_id, index))
        await db.commit()

async def get_test_index(user_id):
     async with aiosqlite.connect(question_data) as db:
        async with db.execute('SELECT question_index FROM test_state WHERE user_id = (?)', (user_id, )) as cursor:
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0

@dp.callback_query(F.data == "right_answer")
async def right_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    current_question_index = await get_test_index(callback.from_user.id)
    await callback.message.answer("Верно!")
    current_question_index += 1
    await update_test_index(callback.from_user.id, current_question_index)
    if current_question_index < len(question_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer("Это был последний вопрос. Тест завершен!")

@dp.callback_query(F.data == "wrong_answer")
async def wrong_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    current_question_index = await get_test_index(callback.from_user.id)
    correct_option = question_data[current_question_index]['correct_option']
    await callback.message.answer(f"Неправильно. Правильный ответ: {question_data[current_question_index]['options'][correct_option]}")
    current_question_index += 1
    await update_test_index(callback.from_user.id, current_question_index)
    if current_question_index < len(question_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer("Это был последний вопрос. Тест завершен!")

async def main():
    await dp.start_polling(bot)
    await create_table()
if __name__ == "__main__":
    asyncio.run(main())