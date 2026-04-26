import asyncio
import random
import logging
import os
from os import getenv

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from motor.motor_asyncio import AsyncIOMotorClient

# --- KONFIGURATSIYA (Railway Variables bo'limidan oladi) ---
BOT_TOKEN = getenv("BOT_TOKEN")
MONGO_URL = getenv("MONGO_URL")
# Admin ID raqam bo'lishi kerak, default 0
ADMIN_ID = int(getenv("ADMIN_ID", 0))

# Token mavjudligini tekshiramiz (Xatolikni aniqlash uchun)
if not BOT_TOKEN:
    raise ValueError("XATO: BOT_TOKEN muhit o'zgaruvchisi topilmadi. Railway 'Variables' bo'limini tekshiring!")

# --- DATABASE SOZLAMALARI ---
client = AsyncIOMotorClient(MONGO_URL)
db = client['anime_bot_db']
users_collection = db['users']

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- FUNKSIYALAR ---
def generate_adk():
    """8 talik random ADK yaratish"""
    digits = "".join([str(random.randint(0, 9)) for _ in range(8)])
    return f"AnICen/{digits}/bot"

async def get_user_rank(points):
    """Ballarga qarab unvon berish"""
    if points >= 10000: return "Anime Afsonasi 👑"
    if points >= 5000: return "Hokage 🔥"
    if points >= 2000: return "Shinobi ⚔️"
    if points >= 500: return "Naruto"
    return "Yangi boshlovchi 🌱"

def main_menu_keyboard():
    """Asosiy menyu tugmalari"""
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="🔍 Anime qidirish", callback_data="search"),
        types.InlineKeyboardButton(text="📂 Janrlar", callback_data="genres")
    )
    builder.row(
        types.InlineKeyboardButton(text="⭐ Tanlanganlar", callback_data="favs"),
        types.InlineKeyboardButton(text="🎲 Tasodifiy anime", callback_data="random")
    )
    builder.row(
        types.InlineKeyboardButton(text="🏆 Top-100", callback_data="top100"),
        types.InlineKeyboardButton(text="⚙️ Sozlamalar", callback_data="settings")
    )
    return builder.as_markup()

# --- HANDLERLAR ---
@dp.message(CommandStart())
async def command_start_handler(message: types.Message):
    user_id = message.from_user.id
    user_data = await users_collection.find_one({"user_id": user_id})

    if not user_data:
        # Birinchi marta kirgan foydalanuvchi
        new_adk = generate_adk()
        await users_collection.insert_one({
            "user_id": user_id,
            "username": message.from_user.username,
            "full_name": message.from_user.full_name,
            "points": 0,
            "adk": new_adk,
            "favorites": [],
            "history": []
        })
        
        text = (f"Salom, {message.from_user.full_name}! 👋\n"
                f"Dunyodagi eng qiziqarli animelar olamiga xush kelibsiz!\n\n"
                f"🔍 Izlash — Sevimli animengizni topishingiz;\n"
                f"⭐ Tanlanganlar — O'zingizga yoqqanlarini saqlashingiz;\n"
                f"🎲 Tasodifiy — Tavsiyalar olishingiz mumkin.\n\n"
                f"Pastdagi tugmalardan birini tanlang:")
        
        builder = InlineKeyboardBuilder()
        builder.row(types.InlineKeyboardButton(text="🆕 ADK YARATISH", callback_data="gen_adk"))
        builder.row(types.InlineKeyboardButton(text="🔑 MENDA ADK BOR", callback_data="have_adk"))
        
        await message.answer(text, reply_markup=builder.as_markup())
    else:
        # Qayta kirgan foydalanuvchi
        points = user_data.get("points", 0)
        rank = await get_user_rank(points)
        adk = user_data.get("adk")
        
        text = (f"Sizni yana koʻrganimizdan xursandmiz! {message.from_user.first_name} 👋\n\n"
                f"🆔: `{user_id}`\n"
                f"ADK: `{adk}`\n\n"
                f"Bugun nima koʻramiz? Tanlanganlar roʻyxatingizda yangi qismlar chiqib qolgan boʻlishi mumkin!\n\n"
                f"Davom etish uchun menyudan kerakli boʻlimni tanlang:")
        
        await message.answer(text, reply_markup=main_menu_keyboard(), parse_mode="Markdown")

@dp.callback_query(F.data == "gen_adk")
async def generate_adk_callback(callback: types.CallbackQuery):
    user_data = await users_collection.find_one({"user_id": callback.from_user.id})
    await callback.message.edit_text(
        f"Sizning shaxsiy ADK kodingiz yaratildi:\n\n`{user_data['adk']}`\n\n"
        "Ushbu kodni saqlab qo'ying, u hisobingizni tiklashga yordam beradi.",
        reply_markup=main_menu_keyboard(),
        parse_mode="Markdown"
    )

# --- BOTNI ISHGA TUSHIRISH ---
async def main():
    # Konfliktni oldini olish uchun drop_pending_updates=True
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
        
