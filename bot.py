import asyncio
import logging
import random
from os import getenv

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from motor.motor_asyncio import AsyncIOMotorClient

# O'zimizning fayldan import
from keyboards import main_menu_keyboard, back_to_main_keyboard

# --- KONFIGURATSIYA ---
BOT_TOKEN = getenv("BOT_TOKEN")
MONGO_URL = getenv("MONGO_URL")

client = AsyncIOMotorClient(MONGO_URL)
db = client['anicen_v2'] # Yangi baza nomi
users_collection = db['users']

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- HANDLERLAR ---

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    
    # Foydalanuvchini bazada tekshirish/yaratish
    user_data = await users_collection.find_one({"user_id": user_id})
    if not user_data:
        await users_collection.insert_one({
            "user_id": user_id,
            "first_name": first_name,
            "points": 50,
            "favorites": [],
            "join_date": datetime.now()
        })

    # Siz bergan vizual dizayn
    welcome_text = (
        f"<b>╔═══ ANICEN ═══╗</b>\n"
        f"   Anime dunyosiga xush kelibsiz\n"
        f"<b>╚═════════════════╝</b>\n\n"
        f"👋 Salom, <b>{first_name}</b>!\n\n"
        f"Siz bu yerda:\n"
        f"👤 Profil ochasiz\n"
        f"🔍 Anime qidirasiz\n"
        f"🎬 Epizodlarni tomosha qilasiz\n"
        f"🌟 Sevimlilarni saqlaysiz\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🔥 Trend animelar sizni kutmoqda!\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"⚡ Boshlash uchun tugmani tanlang:"
    )

    await message.answer(welcome_text, reply_markup=main_menu_keyboard(), parse_mode=ParseMode.HTML)

# --- TUGMALAR UCHUN JAVOBLAR (PLACEHOLDERS) ---

@dp.callback_query(F.data == "profile")
async def profile_call(callback: types.CallbackQuery):
    user_data = await users_collection.find_one({"user_id": callback.from_user.id})
    points = user_data.get("points", 0)
    
    text = (
        f"👤 <b>PROFIL</b>\n\n"
        f"Ism: {callback.from_user.first_name}\n"
        f"Ballar: {points} 🪙\n"
        f"Holat: Faol ✅"
    )
    await callback.message.edit_text(text, reply_markup=back_to_main_keyboard(), parse_mode=ParseMode.HTML)
    await callback.answer()

@dp.callback_query(F.data == "back_main")
async def back_main_call(callback: types.CallbackQuery):
    first_name = callback.from_user.first_name
    welcome_text = (
        f"<b>╔═══ ANICEN ═══╗</b>\n"
        f"   Anime dunyosiga xush kelibsiz\n"
        f"<b>╚═════════════════╝</b>\n\n"
        f"👋 Salom, <b>{first_name}</b>!\n\n"
        f"Siz bu yerda ko'p narsaga ega bo'lasiz.\n\n"
        f"⚡ Boshlash uchun tugmani tanlang:"
    )
    await callback.message.edit_text(welcome_text, reply_markup=main_menu_keyboard(), parse_mode=ParseMode.HTML)
    await callback.answer()

@dp.callback_query(F.data.in_(["search", "top100", "episodes", "favs", "settings"]))
async def functional_calls(callback: types.CallbackQuery):
    await callback.answer("Bu bo'lim keyingi bosqichda ishga tushadi! 🛠", show_alert=True)

# --- ISHGA TUSHIRISH ---
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot to'xtatildi")
    
