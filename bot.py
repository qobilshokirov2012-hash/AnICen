import os
import asyncio
import aiohttp
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from motor.motor_asyncio import AsyncIOMotorClient

# Railway Variables
TOKEN = os.getenv("BOT_TOKEN")
MONGO_URL = os.getenv("MONGO_URL")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0)) # O'zingizning ID-raqamingizni Railway-da kiriting

bot = Bot(token=TOKEN)
dp = Dispatcher()

# MongoDB
client = AsyncIOMotorClient(MONGO_URL)
db = client.anime_bot_db
users_collection = db.users

class UserState(StatesGroup):
    waiting_for_new_adk = State()
    waiting_for_old_adk = State()
    admin_broadcast = State()

# --- PREMIUM EMOJI IDLARI ---
E_NOM = "5886473311637999700"
E_SEARCH = "5888620056551625531"
E_SIFAT = "5850392884817172292"
E_TAG = "5890883384057533697"
E_USER = "5938196735200333756"
E_SHARE = "6039539366177541657"
E_SILENT = "6039853100653612987"
E_COMMAND = "5962952497197748583"

# --- YORDAMCHI FUNKSIYALAR ---
async def translate_to_uz(text):
    if not text: return "Ma'lumot topilmadi."
    url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=uz&dt=t&q={text}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return "".join([i[0] for i in data[0]])
            return text

async def get_anime_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data.get('data')
            return None

def get_main_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="🎲 Tasodifiy Anime"), types.KeyboardButton(text="🔥 Top Animelar"))
    builder.row(types.KeyboardButton(text="❤️ Tanlanganlar"), types.KeyboardButton(text="🎭 Janrlar"))
    return builder.as_markup(resize_keyboard=True)

# --- START & ADK TIZIMI ---
@dp.message(Command("start"))
async def start_cmd(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = await users_collection.find_one({"user_id": user_id})
    
    if not user or "adk" not in user:
        kb = InlineKeyboardBuilder()
        kb.add(types.InlineKeyboardButton(text="Yangi ADK yaratish ✨", callback_data="create_adk"))
        kb.add(types.InlineKeyboardButton(text="Menda ADK bor 💎", callback_data="have_adk"))
        await message.answer(f"Salom! Botdan foydalanish uchun ADK yarating:", reply_markup=kb.as_markup())
    else:
        await message.answer(f"Xush kelibsiz! Anime qidirishni boshlang.", reply_markup=get_main_menu())

@dp.message(Command("ADK"))
async def profile_cmd(message: types.Message):
    user = await users_collection.find_one({"user_id": message.from_user.id})
    if not user or "adk" not in user:
        await message.answer("Sizda hali ADK yo'q. /start bosing.")
        return
    
    faves_count = len(user.get("favorites", []))
    text = (
        f'<tg-emoji emoji-id="{E_USER}">👤</tg-emoji> <b>Profil:</b>\n'
        f"🆔 ID: <code>{message.from_user.id}</code>\n"
        f"💎 ADK: <code>{user['adk']}</code>\n"
        f"❤️ Saqlanganlar: {faves_count} ta"
    )
    await message.answer(text, parse_mode="HTML")

# --- MENU TUGMALARI ISHLOVCHILARI ---
@dp.message(F.text == "🎲 Tasodifiy Anime")
async def random_anime(message: types.Message):
    data = await get_anime_data("https://api.jikan.moe/v4/random/anime")
    if data: await send_anime_info(message, data)

@dp.message(F.text == "🔥 Top Animelar")
async def top_animelar(message: types.Message):
    data = await get_anime_data("https://api.jikan.moe/v4/top/anime?limit=5")
    for anime in data:
        await send_anime_info(message, anime)

@dp.message(F.text == "🎭 Janrlar")
async def show_genres(message: types.Message):
    genres = {"Jangari": 1, "Sarguzasht": 2, "Komediya": 4, "Drama": 8, "Dahshat": 14}
    kb = InlineKeyboardBuilder()
    for name, id in genres.items():
        kb.add(types.InlineKeyboardButton(text=name, callback_data=f"genre_{id}"))
    kb.adjust(2)
    await message.answer("Janrni tanlang:", reply_markup=kb.as_markup())

@dp.message(F.text == "❤️ Tanlanganlar")
async def show_favorites(message: types.Message):
    user = await users_collection.find_one({"user_id": message.from_user.id})
    faves = user.get("favorites", [])
    if not faves:
        await message.answer("Sizda hali saqlangan animelar yo'q.")
        return
    
    text = "❤️ <b>Sizning tanlanganlaringiz:</b>\n\n"
    for item in faves[-10:]: # Oxirgi 10 tasini ko'rsatadi
        text += f"• {item['title']}\n"
    await message.answer(text, parse_mode="HTML")

# --- ANIME QIDIRUV VA YUBORISH ---
async def send_anime_info(message, anime):
    title = anime['title']
    score = anime.get('score', 'N/A')
    image_url = anime['images']['jpg']['large_image_url']
    synopsis_uz = await translate_to_uz(anime.get('synopsis', '')[:400])
    
    caption = (
        f'<tg-emoji emoji-id="{E_NOM}">📝</tg-emoji> <b>Nomi:</b> {title}\n'
        f'<tg-emoji emoji-id="{E_SIFAT}">⭐</tg-emoji> <b>Reyting:</b> {score}\n\n'
        f'<i>{synopsis_uz}</i>'
    )
    
    kb = InlineKeyboardBuilder()
    kb.add(types.InlineKeyboardButton(text="❤️ Saqlash", callback_data=f"fave_{anime['mal_id']}"))
    kb.add(types.InlineKeyboardButton(text="📢 Ulashish", switch_inline_query=title))
    
    await message.answer_photo(photo=image_url, caption=caption, parse_mode="HTML", reply_markup=kb.as_markup())

@dp.message(F.text)
async def handle_search(message: types.Message):
    if message.text.startswith("/") or message.text in ["🎲 Tasodifiy Anime", "🔥 Top Animelar", "❤️ Tanlanganlar", "🎭 Janrlar"]: return
    
    user = await users_collection.find_one({"user_id": message.from_user.id})
    if not user or "adk" not in user: return
    
    data = await get_anime_data(f"https://api.jikan.moe/v4/anime?q={message.text}&limit=1")
    if data: await send_anime_info(message, data[0])
    else: await message.answer("Hech narsa topilmadi ❌")

# --- CALLBACKLAR (SAVE, GENRE, ADK) ---
@dp.callback_query(F.data.startswith("fave_"))
async def save_favorite(callback: types.CallbackQuery):
    anime_id = callback.data.split("_")[1]
    # Anime nomini olish uchun API ga murojaat (oddiyroq bo'lishi uchun title ni bazaga yozamiz)
    await users_collection.update_one(
        {"user_id": callback.from_user.id},
        {"$addToSet": {"favorites": {"mal_id": anime_id, "title": "Anime"}}}
    )
    await callback.answer("Tanlanganlarga qo'shildi! ❤️")

@dp.callback_query(F.data.startswith("genre_"))
async def genre_search(callback: types.CallbackQuery):
    genre_id = callback.data.split("_")[1]
    data = await get_anime_data(f"https://api.jikan.moe/v4/anime?genres={genre_id}&limit=3&order_by=score&sort=desc")
    for anime in data:
        await send_anime_info(callback.message, anime)
    await callback.answer()

# --- ADMIN PANEL ---
@dp.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    
    count = await users_collection.count_documents({})
    kb = InlineKeyboardBuilder()
    kb.add(types.InlineKeyboardButton(text="Xabar yuborish 📢", callback_data="admin_post"))
    await message.answer(f"📊 <b>Statistika:</b>\nJami foydalanuvchilar: {count} ta", parse_mode="HTML", reply_markup=kb.as_markup())

@dp.callback_query(F.data == "admin_post")
async def admin_post_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Barcha foydalanuvchilarga yuboriladigan xabarni yozing:")
    await state.set_state(UserState.admin_broadcast)

@dp.message(UserState.admin_broadcast)
async def admin_broadcast_send(message: types.Message, state: FSMContext):
    users = users_collection.find({})
    count = 0
    async for user in users:
        try:
            await bot.send_message(user['user_id'], message.text)
            count += 1
        except: pass
    await message.answer(f"Xabar {count} ta foydalanuvchiga yuborildi ✅")
    await state.clear()

# --- ADK CREATION LOGIC (START DAN) ---
@dp.callback_query(F.data == "create_adk")
async def cb_create(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("8 ta raqam yuboring:")
    await state.set_state(UserState.waiting_for_new_adk)

@dp.message(UserState.waiting_for_new_adk)
async def proc_new(message: types.Message, state: FSMContext):
    if len(message.text) == 8 and message.text.isdigit():
        adk = f"AnICen/{message.text}/bot"
        if await users_collection.find_one({"adk": adk}):
            await message.answer("Band! Boshqa raqam:")
            return
        await users_collection.update_one({"user_id": message.from_user.id}, 
            {"$set": {"adk": adk, "first_name": message.from_user.first_name, "favorites": []}}, upsert=True)
        await message.answer(f"Tayyor! ADK: {adk}", reply_markup=get_main_menu())
        await state.clear()

# (Qolgan 'have_adk' mantiqlari ham shunday davom etadi...)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
