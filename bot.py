import asyncio
import logging
import random
from os import getenv
from datetime import datetime

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from motor.motor_asyncio import AsyncIOMotorClient

# Tugmalarni import qilish
from keyboards import main_menu_keyboard

# --- KONFIGURATSIYA ---
BOT_TOKEN = getenv("BOT_TOKEN")
MONGO_URL = getenv("MONGO_URL")

client = AsyncIOMotorClient(MONGO_URL)
db = client['anicen_v2']
users_collection = db['users']

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- START HANDLER ---
@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    
    # Bazada tekshirish
    user_data = await users_collection.find_one({"user_id": user_id})
    if not user_data:
        await users_collection.insert_one({
            "user_id": user_id,
            "first_name": first_name,
            "points": 50,
            "favorites": [],
            "join_date": datetime.now()
        })

    # Siz bergan vizual dizayn + Emoji IDlar
    welcome_text = (
        f"<tg-emoji emoji-id='6028282982744202450'>╔═══ ANICEN ═══╗</tg-emoji>\n"
        f"   Anime dunyosiga xush kelibsiz\n"
        f"<tg-emoji emoji-id='6028282982744202450'>╚═════════════════╝</tg-emoji>\n\n"
        f"<tg-emoji emoji-id='5784885558287276809'>👋</tg-emoji> Salom, <b>{first_name}</b>!\n\n"
        f"Siz bu yerda:\n"
        f"<tg-emoji emoji-id='5332724926216428039'>👤</tg-emoji> Profil ochasiz\n"
        f"<tg-emoji emoji-id='5348282577662778261'>🔍</tg-emoji> Anime qidirasiz\n"
        f"<tg-emoji emoji-id='6325682031741109665'>🎬</tg-emoji> Epizodlarni tomosha qilasiz\n"
        f"<tg-emoji emoji-id='5361979846845014099'>🌟</tg-emoji> Sevimlilarni saqlaysiz\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"<tg-emoji emoji-id='5352743837502545676'>🔥</tg-emoji> Trend animelar sizni kutmoqda!\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"<tg-emoji emoji-id='5332722143077613679'>⚡</tg-emoji> Boshlash uchun tugmani tanlang:"
    )

    await message.answer(welcome_text, reply_markup=main_menu_keyboard(), parse_mode=ParseMode.HTML)

# --- BOTNI ISHGA TUSHIRISH ---
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot to'xtatildi")
        
