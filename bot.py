import asyncio
import random
import logging
from datetime import datetime
from os import getenv

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from motor.motor_asyncio import AsyncIOMotorClient

# O'zingiz yaratgan fayllardan import
from keyboards import *

# --- KONFIGURATSIYA ---
BOT_TOKEN = getenv("BOT_TOKEN")
MONGO_URL = getenv("MONGO_URL")

client = AsyncIOMotorClient(MONGO_URL)
db = client['anime_bot_db']
users_collection = db['users']

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- STATES ---
class BotStates(StatesGroup):
    waiting_for_adk = State()
    ai_chatting = State() 

# --- AI JAVOBLARI ---
itachi_quotes = [
    "Odamlar o'z haqiqatlarini noto'g'ri tushunchalar asosida qurishadi.",
    "Kuchli bo'lish hamma narsani hal qilmaydi.",
    "Qishloqning qorong'u qismini men o'z zimmamga olganman."
]
levi_quotes = [
    "Hech qanday tanlov afsuslarsiz bo'lmaydi.",
    "O'zingga ishon yoki o'zgalarga, baribir natija noma'lum.",
    "Vaqtingni bekorga sarflama, ishga kirish."
]

# --- START HANDLER ---
@dp.message(CommandStart())
async def start(message: types.Message):
    user_id = message.from_user.id
    user_data = await users_collection.find_one({"user_id": user_id})

    if not user_data:
        new_adk = f"AnICen/{random.randint(10000000, 99999999)}/bot"
        await users_collection.insert_one({
            "user_id": user_id,
            "username": message.from_user.username,
            "points": 50, 
            "adk": new_adk,
            "notifications": True,
            "rank": "Yangi boshlovchi 🌱"
        })
        await message.answer(f"Salom! Sizga 50 🪙 bonus berildi.\nADK: <code>{new_adk}</code>", 
                             reply_markup=main_menu_keyboard(), parse_mode="HTML")
    else:
        await message.answer("Xush kelibsiz! Bugun nima ko'ramiz?", reply_markup=main_menu_keyboard())

# --- AI CHAT BO'LIMI ---
@dp.callback_query(F.data == "ai_chat")
async def ai_menu(callback: types.CallbackQuery):
    await callback.message.edit_text("Qaysi personaj bilan suhbatlashmoqchisiz?", 
                                     reply_markup=ai_characters_keyboard())
    await callback.answer()

@dp.callback_query(F.data.startswith("chat_"))
async def start_chat(callback: types.CallbackQuery, state: FSMContext):
    char = callback.data.split("_")[1]
    await state.update_data(character=char)
    await callback.message.answer(f"Siz {char.capitalize()} bilan suhbatni boshladingiz. \nXabar yozing (to'xtatish uchun /stop):")
    await state.set_state(BotStates.ai_chatting)
    await callback.answer()

@dp.message(BotStates.ai_chatting)
async def ai_reply(message: types.Message, state: FSMContext):
    if message.text == "/stop":
        await state.clear()
        await message.answer("Suhbat yakunlandi.", reply_markup=main_menu_keyboard())
        return
    
    data = await state.get_data()
    char = data.get("character")
    reply = random.choice(itachi_quotes if char == "itachi" else levi_quotes)
    await message.answer(f"<b>{char.capitalize()}:</b> {reply}", parse_mode="HTML")

# --- PROFIL ---
@dp.callback_query(F.data == "profile")
async def profile_handler(callback: types.CallbackQuery):
    user_data = await users_collection.find_one({"user_id": callback.from_user.id})
    points = user_data.get("points", 0)
    adk = user_data.get("adk", "Noma'lum")
    
    text = (
        f"👤 <b>PROFILINGIZ</b>\n\n"
        f"💰 Ballar: <b>{points} 🪙</b>\n"
        f"🔑 ADK: <code>{adk}</code>\n\n"
        f"<i>Ballaringizni oshirish uchun faol bo'ling!</i>"
    )
    await callback.message.edit_text(text, reply_markup=profile_keyboard(), parse_mode="HTML")
    await callback.answer()

# --- SOZLAMALAR ---
@dp.callback_query(F.data == "settings")
async def settings_handler(callback: types.CallbackQuery):
    user_data = await users_collection.find_one({"user_id": callback.from_user.id})
    notif_status = user_data.get("notifications", True)
    
    await callback.message.edit_text(
        "⚙️ <b>Sozlamalar</b>\n\nBotni o'zingizga moslang:",
        reply_markup=settings_keyboard(notifications_on=notif_status),
        parse_mode="HTML"
    )
    await callback.answer()

@dp.callback_query(F.data == "toggle_notif")
async def toggle_notifications(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user_data = await users_collection.find_one({"user_id": user_id})
    current_status = user_data.get("notifications", True)
    new_status = not current_status
    
    await users_collection.update_one({"user_id": user_id}, {"$set": {"notifications": new_status}})
    await callback.message.edit_reply_markup(reply_markup=settings_keyboard(notifications_on=new_status))
    
    # XATOLIK TUZATILDI: f-string ichida backslash ishlatmaslik uchun o'zgaruvchiga olindi
    status_msg = "yoqildi ✅" if new_status else "o'chirildi ❌"
    await callback.answer(f"Bildirishnomalar {status_msg}")

# --- DO'KON VA REFERAL ---
@dp.callback_query(F.data == "spend")
async def shop(callback: types.CallbackQuery):
    await callback.message.edit_text("Ballaringizni nimalarga sarflaysiz?", reply_markup=shop_keyboard())
    await callback.answer()

@dp.callback_query(F.data == "referral")
async def ref_link(callback: types.CallbackQuery):
    link = f"https://t.me/AnICenXBot?start={callback.from_user.id}"
    await callback.message.answer(f"Do'stlaringizni taklif qiling va 50 🪙 yuting!\n\nSizning havolangiz:\n{link}")
    await callback.answer()

@dp.callback_query(F.data == "back_main")
async def back(callback: types.CallbackQuery):
    await callback.message.edit_text("Asosiy menyu:", reply_markup=main_menu_keyboard())
    await callback.answer()

# --- BOTNI ISHGA TUSHIRISH ---
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot to'xtatildi")
    
