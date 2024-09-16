import asyncio
import logging
from test import *
from aiogram import F
from aiogram import types
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder

logging.basicConfig(level=logging.INFO)
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
    user_id = message.from_user.id
    await update_test_index_points(user_id, 0, 0)
    await get_question(message, user_id)

@dp.message(F.text=="В меню")
async def cmd_menu(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Тест"))
    builder.add(types.KeyboardButton(text="Статистика"))
    await message.answer("Нажмите 'Тест' для проверки своих знаний.", reply_markup=builder.as_markup(resize_keyboard=True))

@dp.message(F.text=="Статистика")
async def cmd_test(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Моя статистика"))
    builder.add(types.KeyboardButton(text="В меню"))
    await message.answer(f"Статистка!", reply_markup=builder.as_markup(resize_keyboard=True))

async def main():
    await create_table()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main()) 