import asyncio
import logging
from test import *
from aiogram import F
from aiogram import types
from aiogram import Bot, types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder

logging.basicConfig(level=logging.INFO)
API_TOKEN = "7404804929:AAFuXD8pshvqK8JPKFRQY1yiXXDCSGWw3lQ"
bot = Bot(token=API_TOKEN) 

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
    user_id = message.from_user.id
    username = message.from_user.first_name
    await rec_new_user(user_id, username, 0, 0)
    await get_question(message, user_id)
    

@dp.message(F.text=="В меню")
async def cmd_menu(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Тест"))
    builder.add(types.KeyboardButton(text="Статистика"))
    await message.answer("Нажмите 'Тест' для проверки своих знаний.", reply_markup=builder.as_markup(resize_keyboard=True))
    
async def get_stat_users():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT user_id, points FROM test_state ORDER BY points DESC') as cursor:
            results = await cursor.fetchall()
            return results
        
@dp.message(F.text=="Статистика")
async def cmd_test(message: types.Message):
    builder = ReplyKeyboardBuilder()
    #builder.add(types.KeyboardButton(text="Моя статистика")) в разработке
    builder.add(types.KeyboardButton(text="В меню"))
    users = await get_stat_users()
    end_message = await end_message_points(message.from_user.id)

    await message.answer(f"Вы набрали {end_message}.", parse_mode="Markdown", reply_markup=builder.as_markup(resize_keyboard=True))
    position = 1
    for user_id in users:
        end_message = await end_message_points(user_id[0])
        username = await get_username(user_id[0])
        await message.answer(f"{position}. Бариста [{username}](tg://user?id={str(user_id[0])}) набрал(а) {end_message}.", parse_mode="Markdown", reply_markup=builder.as_markup(resize_keyboard=True))
        position += 1


async def main():
    await create_table()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main()) 