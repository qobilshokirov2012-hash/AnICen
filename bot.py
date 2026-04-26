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

# MongoDB ulanishi
client = AsyncIOMotorClient(MONGO_URL)
db = client.anime_bot_db
users_collection = db.users

# ADK holatlarini boshqarish
class UserState(StatesGroup):
    waiting_for_new_adk = State()
    waiting_for_old_adk = State()

# --- SIZ BERGAN PREMIUM EMOJI IDLARI ---
E_NOM = "5886473311637999700"          
E_SEARCH = "5888620056551625531"       
E_SIFAT = "5850392884817172292"        
E_TAG = "5890883384057533697"          
E_USER = "5938196735200333756"         
E_SHARE = "6039539366177541657"        
E_SILENT = "6039853100653612987"
E_COMMAND = "5962952497197748583"      

# Tarjimon funksiyasi
async def translate_to_uz(text):
    if not text:
        return "Ma'lumot topilmadi."
    url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=uz&dt=t&q={text}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return "".join([i[0] for i in data[0]])
            return text

# Anime qidirish
async def search_anime(query):
    url = f"https://api.jikan.moe/v4/anime?q={query}&limit=1"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                if data['data']:
                    return data['data'][0]
            return None

# --- START BUYRUG'I ---
@dp.message(Command("start"))
async def start_cmd(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    
    user = await users_collection.find_one({"user_id": user_id})
    
    user_emoji = f'<tg-emoji emoji-id="{E_USER}">👤</tg-emoji>'
    cmd_emoji = f'<tg-emoji emoji-id="{E_COMMAND}">🆔</tg-emoji>'
    silent_emoji = f'<tg-emoji emoji-id="{E_SILENT}">💎</tg-emoji>'

    if not user or "adk" not in user:
        kb = [
            [types.InlineKeyboardButton(text="Yangi ADK yaratish ✨", callback_data="create_adk")],
            [types.InlineKeyboardButton(text="Menda ADK bor 💎", callback_data="have_adk")]
        ]
        markup = types.InlineKeyboardMarkup(inline_keyboard=kb)
        
        text = (
            f"{user_emoji} <b>Xush kelibsiz, {first_name}!</b>\n"
            f"{cmd_emoji} <b>Sizning Telegram ID:</b> <code>{user_id}</code>\n\n"
            f"Botdan foydalanish uchun sizda <b>ADK (AnICen ID KOD)</b> bo'lishi kerak.\n"
            f"Iltimos, quyidagilardan birini tanlang:"
        )
        await message.answer(text, parse_mode="HTML", reply_markup=markup)
    else:
        text = (
            f"{user_emoji} <b>Qayta ko'rishganimizdan xursandman, {first_name}!</b>\n"
            f"{cmd_emoji} <b>Telegram ID:</b> <code>{user_id}</code>\n"
            f"{silent_emoji} <b>Sizning ADK:</b> <code>{user['adk']}</code>\n\n"
            f"Anime qidirish uchun shunchaki nomini yozing! 🎬"
        )
        await message.answer(text, parse_mode="HTML")

# --- CALLBACK TUGMALAR ---
@dp.callback_query(F.data == "create_adk")
async def create_adk_step(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Yangi ADK yaratish uchun <b>8 ta raqam</b> yuboring:\n(Masalan: 12345678)", parse_mode="HTML")
    await state.set_state(UserState.waiting_for_new_adk)

@dp.callback_query(F.data == "have_adk")
async def have_adk_step(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Iltimos, eski <b>ADK kodingizni</b> to'liq kiriting:\n(Masalan: AnICen/12345678/bot)", parse_mode="HTML")
    await state.set_state(UserState.waiting_for_old_adk)

# --- ADK JARAYONLARI ---
@dp.message(UserState.waiting_for_new_adk)
async def process_new_adk(message: types.Message, state: FSMContext):
    if len(message.text) == 8 and message.text.isdigit():
        adk_code = f"AnICen/{message.text}/bot"
        
        # Bazada bor-yo'qligini tekshirish
        existing_adk = await users_collection.find_one({"adk": adk_code})
        if existing_adk:
            await message.answer("❌ Kechirasiz, bu raqam allaqachon band! Boshqa 8 ta raqam yozing.")
            return

        # Saqlash
        await users_collection.update_one(
            {"user_id": message.from_user.id},
            {"$set": {
                "user_id": message.from_user.id,
                "first_name": message.from_user.first_name,
                "username": message.from_user.username,
                "adk": adk_code
            }}, upsert=True
        )
        await message.answer(f"✅ Tabriklayman! Yangi ADK yaratildi:\n<code>{adk_code}</code>\n\nEndi bemalol anime qidirishingiz mumkin!", parse_mode="HTML")
        await state.clear()
    else:
        await message.answer("❌ Xato! Faqat 8 ta raqamdan iborat kod yuboring. (Masalan: 12345678)")

@dp.message(UserState.waiting_for_old_adk)
async def process_old_adk(message: types.Message, state: FSMContext):
    if re.match(r"AnICen/\d{8}/bot", message.text):
        existing_adk = await users_collection.find_one({"adk": message.text})
        
        if not existing_adk:
            await message.answer("❌ Bunday ADK bazada topilmadi!\nKodingizni to'g'ri yozganingizni tekshiring yoki /start bosib yangisini yarating.")
            return

        # Eski ADK bo'lsa, joriy akkauntga biriktirish
        await users_collection.update_one(
            {"user_id": message.from_user.id},
            {"$set": {
                "user_id": message.from_user.id,
                "first_name": message.from_user.first_name,
                "username": message.from_user.username,
                "adk": message.text
            }}, upsert=True
        )
        await message.answer(f"💎 ADK muvaffaqiyatli ulandi!\nSizning kodingiz: <code>{message.text}</code>\n\nEndi anime qidirishingiz mumkin.", parse_mode="HTML")
        await state.clear()
    else:
        await message.answer("❌ Xato format! Kod mana bunday bo'lishi kerak: <code>AnICen/12345678/bot</code>", parse_mode="HTML")

# --- ANIME QIDIRUV ---
@dp.message(F.text)
async def handle_anime_search(message: types.Message):
    if message.text.startswith("/"): return
    
    # Foydalanuvchida ADK bor-yo'qligini tekshirish
    user = await users_collection.find_one({"user_id": message.from_user.id})
    if not user or "adk" not in user:
        await message.answer("⚠️ Iltimos, anime qidirishdan oldin /start buyrug'ini bosib ADK yarating yoki kiritib o'ting!")
        return

    search_emoji = f'<tg-emoji emoji-id="{E_SEARCH}">🔎</tg-emoji>'
    msg = await message.answer(f"Qidiryapman... {search_emoji}", parse_mode="HTML")
    
    anime = await search_anime(message.text)
    
    if anime:
        title = anime['title']
        score = anime.get('score', 'Noma’lum')
        image_url = anime['images']['jpg']['large_image_url']
        synopsis_en = anime.get('synopsis', 'Ma\'lumot yo\'q.')
        
        synopsis_uz = await translate_to_uz(synopsis_en[:500])
        
        nom_emoji = f'<tg-emoji emoji-id="{E_NOM}">📝</tg-emoji>'
        sifat_emoji = f'<tg-emoji emoji-id="{E_SIFAT}">⭐</tg-emoji>'
        tag_emoji = f'<tg-emoji emoji-id="{E_TAG}">🏷</tg-emoji>'
        silent_emoji = f'<tg-emoji emoji-id="{E_SILENT}">🔇</tg-emoji>'
        
        caption = (
            f"{nom_emoji} <b>Nomi:</b> {title} {silent_emoji}\n"
            f"{sifat_emoji} <b>Reyting:</b> {score}\n\n"
            f"{tag_emoji} <b>Annotatsiya:</b>\n<i>{synopsis_uz}</i>"
        )
        
        kb = [[types.InlineKeyboardButton(text="Do'stlarga ulashish", switch_inline_query=title)]]
        markup = types.InlineKeyboardMarkup(inline_keyboard=kb)
        
        await message.answer_photo(photo=image_url, caption=caption, parse_mode="HTML", reply_markup=markup)
        await msg.delete()
    else:
        await msg.edit_text("Afsuski, bunday anime topilmadi. ❌")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    print("Bot muvaffaqiyatli ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
        
