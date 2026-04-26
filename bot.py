import asyncio
import random
import logging
import os
from os import getenv

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from motor.motor_asyncio import AsyncIOMotorClient

# --- KONFIGURATSIYA ---
BOT_TOKEN = getenv("BOT_TOKEN")
MONGO_URL = getenv("MONGO_URL")
ADMIN_ID = int(getenv("ADMIN_ID", 0))

# --- DATABASE ---
client = AsyncIOMotorClient(MONGO_URL)
db = client['anime_bot_db']
users_collection = db['users']

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- STATES ---
class Registration(StatesGroup):
    waiting_for_adk = State()

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
    """Asosiy menyu tugmalari (Bloklarga bo'lingan)"""
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
    builder.row(
        types.InlineKeyboardButton(text="👤 Profil", callback_data="profile")
    )
    return builder.as_markup()

# --- HANDLERLAR ---

@dp.message(CommandStart())
async def command_start_handler(message: types.Message):
    user_id = message.from_user.id
    user_data = await users_collection.find_one({"user_id": user_id})

    if not user_data:
        # Yangi foydalanuvchi
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
        
        # HTML formatida xabar (Xatolik bermasligi uchun)
        text = (f"Salom, <b>{message.from_user.first_name}</b>! 👋\n"
                f"Dunyodagi eng qiziqarli animelar olamiga xush kelibsiz!\n\n"
                f"🔍 <b>Izlash</b> — Sevimli animengizni topishingiz;\n"
                f"⭐ <b>Tanlanganlar</b> — O'zingizga yoqqanlarini saqlashingiz;\n"
                f"🎲 <b>Tasodifiy</b> — Tavsiyalar olishingiz mumkin.\n\n"
                f"Pastdagi tugmalardan birini tanlang:")
        
        builder = InlineKeyboardBuilder()
        builder.row(types.InlineKeyboardButton(text="🆕 ADK YARATISH", callback_data="gen_adk"))
        builder.row(types.InlineKeyboardButton(text="🔑 MENDA ADK BOR", callback_data="have_adk"))
        
        await message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    else:
        # Qayta kirgan foydalanuvchi
        points = user_data.get("points", 0)
        rank = await get_user_rank(points)
        adk = user_data.get("adk")
        
        text = (f"Sizni yana koʻrganimizdan xursandmiz! <b>{message.from_user.first_name}</b> 👋\n"
                f"🆔: <code>{user_id}</code>\n"
                f"ADK: <code>{adk}</code>\n\n"
                f"Bugun nima koʻramiz? Davom etish uchun menyudan bo'limni tanlang:")
        
        await message.answer(text, reply_markup=main_menu_keyboard(), parse_mode="HTML")

@dp.callback_query(F.data == "gen_adk")
async def generate_adk_callback(callback: types.CallbackQuery):
    user_data = await users_collection.find_one({"user_id": callback.from_user.id})
    await callback.message.edit_text(
        f"Sizning shaxsiy ADK kodingiz yaratildi:\n\n<code>{user_data['adk']}</code>\n\n"
        "Ushbu kodni saqlab qo'ying, u hisobingizni tiklashga yordam beradi.",
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML"
    )

@dp.callback_query(F.data == "profile")
async def profile_handler(callback: types.CallbackQuery):
    user_data = await users_collection.find_one({"user_id": callback.from_user.id})
    points = user_data.get("points", 0)
    rank = await get_user_rank(points)
    
    text = (f"👤 <b>Foydalanuvchi Profili</b>\n\n"
            f"Ism: {callback.from_user.full_name}\n"
            f"Daraja: {rank}\n"
            f"Jami ballar: {points} 🪙\n"
            f"🔑 ADK: <code>{user_data['adk']}</code>")
    
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_main"))
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")

@dp.callback_query(F.data == "back_main")
async def back_main(callback: types.CallbackQuery):
    await callback.message.edit_text("Asosiy menyu:", reply_markup=main_menu_keyboard())

# --- ADK TIKLASH MANTIQI ---
@dp.callback_query(F.data == "have_adk")
async def have_adk_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Iltimos, shaxsiy ADK kodingizni yuboring:")
    await state.set_state(Registration.waiting_for_adk)

@dp.message(Registration.waiting_for_adk)
async def process_adk(message: types.Message, state: FSMContext):
    input_adk = message.text.strip()
    old_user_data = await users_collection.find_one({"adk": input_adk})

    if old_user_data:
        # Yangi IDga bog'lash
        await users_collection.update_one(
            {"adk": input_adk},
            {"$set": {"user_id": message.from_user.id}}
        )
        await message.answer("✅ Hisobingiz tiklandi!", reply_markup=main_menu_keyboard())
        await state.clear()
    else:
        await message.answer("❌ Bunday ADK topilmadi.")

# --- BOTNI ISHGA TUSHIRISH ---
async def main():
    # Konfliktni oldini olish
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
