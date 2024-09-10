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
@dp.message(Command("test"))
async def cmd_test(message: types.Message):
    await message.answer(f"Давайте начнем тест!")
    await new_test(message)

async def main():
    await dp.start_polling(bot)
    await create_table()

if __name__ == "__main__":
    asyncio.run(main()) 