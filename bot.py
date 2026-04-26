import os
import asyncio
import aiohttp
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from motor.motor_asyncio import AsyncIOMotorClient

# Railway Variables
TOKEN = os.getenv("BOT_TOKEN")
MONGO_URL = os.getenv("MONGO_URL")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# MongoDB
client = AsyncIOMotorClient(MONGO_URL)
db = client.anime_bot_db
users_collection = db.users

# Holatlarni boshqarish (ADK yaratish yoki kiritish uchun)
class UserState(StatesGroup):
    waiting_for_new_adk = State()
    waiting_for_old_adk = State()

# Siz bergan IDlar
E_USER = "5938196735200333756"
E_NOM = "5886473311637999700"
E_SEARCH = "5888620056551625531"
E_TAG = "5890883384057533697"

@dp.message(Command("start"))
async def start_cmd(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = await users_collection.find_one({"user_id": user_id})
    user_emoji = f'<tg-emoji emoji-id="{E_USER}">👤</tg-emoji>'

    if not user or "adk" not in user:
        # Yangi foydalanuvchi yoki ADKsi yo'qlar uchun
        kb = [
            [types.InlineKeyboardButton(text="Yangi ADK yaratish ✨", callback_data="create_adk")],
            [types.InlineKeyboardButton(text="Menda ADK bor 💎", callback_data="have_adk")]
        ]
        markup = types.InlineKeyboardMarkup(inline_keyboard=kb)
        await message.answer(
            f"{user_emoji} <b>Xush kelibsiz!</b>\n\nBotdan foydalanish uchun sizda <b>ADK (AnICen ID KOD)</b> bo'lishi kerak.\n"
            "Iltimos, tanlang:", 
            parse_mode="HTML", reply_markup=markup
        )
    else:
        await message.answer(
            f"{user_emoji} <b>Xush kelibsiz, {user['first_name']}!</b>\n"
            f"Sizning ADK: <code>{user['adk']}</code>\n\n"
            "Anime qidirish uchun nomini yozing!", parse_mode="HTML"
        )

# Callback handlerlar
@dp.callback_query(F.data == "create_adk")
async def create_adk_step(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Yangi ADK yaratish uchun <b>8 ta raqam</b> yuboring:\n(Masalan: 12345678)", parse_mode="HTML")
    await state.set_state(UserState.waiting_for_new_adk)

@dp.callback_query(F.data == "have_adk")
async def have_adk_step(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Iltimos, eski <b>ADK kodingizni</b> to'liq kiriting:\n(Masalan: AnICen/12345678/bot)", parse_mode="HTML")
    await state.set_state(UserState.waiting_for_old_adk)

# ADK yaratishni qayta ishlash
@dp.message(UserState.waiting_for_new_adk)
async def process_new_adk(message: types.Message, state: FSMContext):
    if len(message.text) == 8 and message.text.isdigit():
        adk_code = f"AnICen/{message.text}/bot"
        await users_collection.update_one(
            {"user_id": message.from_user.id},
            {"$set": {
                "user_id": message.from_user.id,
                "first_name": message.from_user.first_name,
                "adk": adk_code
            }}, upsert=True
        )
        await message.answer(f"✅ Tabriklayman! Yangi ADK yaratildi:\n<code>{adk_code}</code>", parse_mode="HTML")
        await state.clear()
    else:
        await message.answer("Xato! Faqat 8 ta raqamdan iborat kod yuboring.")

# Eski ADKni tekshirish
@dp.message(UserState.waiting_for_old_adk)
async def process_old_adk(message: types.Message, state: FSMContext):
    if re.match(r"AnICen/\d{8}/bot", message.text):
        await users_collection.update_one(
            {"user_id": message.from_user.id},
            {"$set": {
                "user_id": message.from_user.id,
                "first_name": message.from_user.first_name,
                "adk": message.text
            }}, upsert=True
        )
        await message.answer(f"💎 ADK muvaffaqiyatli ulandi!\nSizning kodingiz: <code>{message.text}</code>", parse_mode="HTML")
        await state.clear()
    else:
        await message.answer("Xato format! Kod mana bunday bo'lishi kerak: <code>AnICen/12345678/bot</code>", parse_mode="HTML")

# Anime qidiruv qismi (Oldingi kod kabi qoladi)
# ... (Bu yerda handle_anime_search funksiyasi turadi)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
                          
