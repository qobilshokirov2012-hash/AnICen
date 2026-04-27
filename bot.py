import asyncio
import logging
from datetime import datetime, timezone
from os import getenv

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode
from motor.motor_asyncio import AsyncIOMotorClient

# main_reply_keyboard'ni ham import qilamiz
from keyboards import main_menu_keyboard, main_reply_keyboard, back_to_main_keyboard
from config import EMOJIS

# --- KONFIGURATSIYA ---
BOT_TOKEN = getenv("BOT_TOKEN")
MONGO_URL = getenv("MONGO_URL")

client = AsyncIOMotorClient(MONGO_URL)
db = client['anicen_v2']
users_collection = db['users']

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    try:
        user_id = message.from_user.id
        first_name = message.from_user.first_name
        
        user_data = await users_collection.find_one({"user_id": user_id})
        
        if not user_data:
            await users_collection.insert_one({
                "user_id": user_id,
                "first_name": first_name,
                "points": 50,
                "favorites": [],
                "join_date": datetime.now(timezone.utc)
            })
            
        welcome_text = (
            f"<b>╔═══ANICEN═══╗</b>\n"
            f"<b>╚═══════════╝</b>\n\n"
            f"<tg-emoji emoji-id='{EMOJIS['welcome']}'>👋</tg-emoji> Salom, <b>{first_name}</b>!\n\n"
            f"Siz bu yerda:\n"
            f"<tg-emoji emoji-id='{EMOJIS['profile']}'>👤</tg-emoji> Profil ochasiz\n"
            f"<tg-emoji emoji-id='{EMOJIS['search']}'>🔍</tg-emoji> Anime qidirasiz\n"
            f"<tg-emoji emoji-id='{EMOJIS['episodes']}'>🎬</tg-emoji> Epizodlarni tomosha qilasiz\n"
            f"<tg-emoji emoji-id='{EMOJIS['favorite']}'>🌟</tg-emoji> Sevimlilarni saqlaysiz\n\n"
            f"━━━━━━━━━━━━━━━\n"
            f"<tg-emoji emoji-id='{EMOJIS['trend']}'>🔥</tg-emoji> Trend animelar sizni kutmoqda!\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"<tg-emoji emoji-id='{EMOJIS['start']}'>⚡</tg-emoji> Boshlash uchun tugmani tanlang:"
        )

        # Bu yerda reply_markup o'zgardi: Endi pastdagi doimiy menyu chiqadi
        await message.answer(welcome_text, reply_markup=main_reply_keyboard(), parse_mode=ParseMode.HTML)

    except Exception as e:
        logging.error(f"Xatolik: {e}")

# --- REPLY MENYU TUGMALARI UCHUN HANDLERLAR ---
# Bu qismlar tugmalar bosilganda javob berishi uchun kerak

@dp.message(F.text == "🔍 Qidirish")
async def search_handler(message: types.Message):
    await message.answer("🔍 Anime nomini kiriting:", reply_markup=back_to_main_keyboard())

@dp.message(F.text == "👤 Profil")
async def profile_handler(message: types.Message):
    # Siz aytgan /ADK buyrug'ini shu yerda chaqiramiz
    user_data = await users_collection.find_one({"user_id": message.from_user.id})
    points = user_data.get("points", 0) if user_data else 0
    await message.answer(f"👤 <b>Profilingiz</b>\n\n💰 Ballaringiz: {points} ball\nBuyruq: /ADK", parse_mode=ParseMode.HTML)

@dp.message(Command("ADK"))
async def adk_handler(message: types.Message):
    # /ADK buyrug'i uchun alohida handler
    await profile_handler(message)

@dp.message(F.text == "🎲 Tasodifiy Anime")
async def random_handler(message: types.Message):
    await message.answer("🎲 Tasodifiy anime qidirilmoqda...")

# Profil callback uchun (Inline tugma bosilsa)
@dp.callback_query(F.data == "cmd_adk")
async def profile_via_adk(callback: types.CallbackQuery):
    await callback.answer("Profilingizni ko'rish uchun /ADK buyrug'ini yuboring!", show_alert=True)

# --- ISHGA TUSHIRISH ---
async def main():
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as e:
        logging.critical(f"Botni ishga tushirishda xato: {e}")

if __name__ == "__main__":
    asyncio.run(main())
        
