import os
import asyncio
from aiogram import Bot, Dispatcher, types
from motor.motor_asyncio import AsyncIOMotorClient

# Railway Variables'dan ma'lumotlarni olish
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
MONGO_URL = os.getenv("MONGO_URL") # MongoDB ulanish manzili

bot = Bot(token=TOKEN)
dp = Dispatcher()

# MongoDB ulanishi
client = AsyncIOMotorClient(MONGO_URL)
db = client.anime_bot_db

@dp.message()
async def start_handler(message: types.Message):
    if message.text == "/start":
        await message.answer("Salom! Anime botga xush kelibsiz. Tez orada bu yerda anime qidirish mumkin bo'ladi!")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
  
