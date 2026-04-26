import asyncio
import random
import logging
from os import getenv

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from motor.motor_asyncio import AsyncIOMotorClient

# Tugmalarni import qilish
from keyboards import main_menu_keyboard, start_registration_keyboard, profile_keyboard

# --- KONFIGURATSIYA ---
BOT_TOKEN = getenv("BOT_TOKEN")
MONGO_URL = getenv("MONGO_URL")

client = AsyncIOMotorClient(MONGO_URL)
db = client['anime_bot_db']
users_collection = db['users']

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

class Registration(StatesGroup):
    waiting_for_adk = State()

# --- FUNKSIYALAR ---
def generate_adk():
    digits = "".join([str(random.randint(0, 9)) for _ in range(8)])
    return f"AnICen/{digits}/bot"

# --- HANDLERLAR ---

@dp.message(CommandStart())
async def command_start_handler(message: types.Message):
    user_id = message.from_user.id
    user_data = await users_collection.find_one({"user_id": user_id})

    if not user_data:
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
        text = (f"Salom, <b>{message.from_user.first_name}</b>! 👋\n"
                f"Animelar olamiga xush kelibsiz!")
        await message.answer(text, reply_markup=start_registration_keyboard(), parse_mode="HTML")
    else:
        await message.answer(f"Xush kelibsiz, <b>{message.from_user.first_name}</b>! 👋", 
                             reply_markup=main_menu_keyboard(), parse_mode="HTML")

@dp.callback_query(F.data == "gen_adk")
async def generate_adk_callback(callback: types.CallbackQuery):
    user_data = await users_collection.find_one({"user_id": callback.from_user.id})
    await callback.message.edit_text(
        f"Sizning ADK kodingiz: <code>{user_data['adk']}</code>",
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer() # Tugma "yopishishi" uchun shart!

@dp.callback_query(F.data == "profile")
async def profile_handler(callback: types.CallbackQuery):
    user_data = await users_collection.find_one({"user_id": callback.from_user.id})
    text = (f"👤 <b>Profil</b>\n\nIsm: {callback.from_user.full_name}\n"
            f"Ballar: {user_data.get('points', 0)} 🪙\n"
            f"ADK: <code>{user_data['adk']}</code>")
    await callback.message.edit_text(text, reply_markup=profile_keyboard(), parse_mode="HTML")
    await callback.answer()

@dp.callback_query(F.data == "back_main")
async def back_main(callback: types.CallbackQuery):
    await callback.message.edit_text("Asosiy menyu:", reply_markup=main_menu_keyboard())
    await callback.answer()

# Bo'sh tugmalar uchun umumiy javob (Xatolik bermasligi uchun)
@dp.callback_query(F.data.in_(["search", "genres", "favs", "random", "top100", "settings"]))
async def placeholder_callback(callback: types.CallbackQuery):
    await callback.answer("Bu bo'lim ustida ish olib borilmoqda... 🚧", show_alert=True)

# --- BOTNI ISHGA TUSHIRISH ---
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
