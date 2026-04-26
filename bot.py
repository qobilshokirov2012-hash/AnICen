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
ADMIN_ID = int(os.getenv("ADMIN_ID", 0)) 

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
E_COMMAND = "5962952497197748583"
E_SILENT = "6039853100653612987"

# --- YORDAMCHI FUNKSIYALAR ---
async def translate_to_uz(text):
    if not text: return "Ma'lumot yo'q."
    url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=uz&dt=t&q={text}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return "".join([i[0] for i in data[0]])
            return text

async def get_anime_by_id(mal_id):
    url = f"https://api.jikan.moe/v4/anime/{mal_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                res = await response.json()
                return res['data']
    return None

def get_main_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="🎲 Tasodifiy Anime"), types.KeyboardButton(text="🔥 Top Animelar"))
    builder.row(types.KeyboardButton(text="❤️ Tanlanganlar"), types.KeyboardButton(text="🎭 Janrlar"))
    return builder.as_markup(resize_keyboard=True)

# --- START VA PROFIL (/ADK) ---
@dp.message(Command("start"))
async def start_cmd(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = await users_collection.find_one({"user_id": user_id})
    
    if not user or "adk" not in user:
        kb = InlineKeyboardBuilder()
        kb.add(types.InlineKeyboardButton(text="Yangi ADK yaratish ✨", callback_data="create_adk"))
        kb.add(types.InlineKeyboardButton(text="Menda ADK bor 💎", callback_data="have_adk"))
        kb.adjust(1)
        await message.answer(
            f"🎬 <b>Xush kelibsiz!</b>\n\nBotdan foydalanish uchun maxsus <b>ADK</b> kodi kerak.\n"
            f"Telegram ID: <code>{user_id}</code>\n\nIltimos, tanlang:",
            parse_mode="HTML", reply_markup=kb.as_markup()
        )
    else:
        await message.answer(f"Xush kelibsiz, {user['first_name']}! 😊\nAnime qidirish uchun nomini yozing.", reply_markup=get_main_menu())

@dp.message(Command("ADK"))
async def profile_cmd(message: types.Message):
    user = await users_collection.find_one({"user_id": message.from_user.id})
    if not user or "adk" not in user:
        await message.answer("Sizda hali ADK yo'q. /start ni bosing.")
        return
    
    faves_count = len(user.get("favorites", []))
    text = (
        f'👤 <b>Sizning Profilingiz:</b>\n\n'
        f'🆔 ID: <code>{message.from_user.id}</code>\n'
        f'💎 ADK: <code>{user["adk"]}</code>\n'
        f'❤️ Tanlangan animelar: {faves_count} ta'
    )
    await message.answer(text, parse_mode="HTML")

# --- TANLANGANLAR PAGINATION ---
@dp.message(F.text == "❤️ Tanlanganlar")
async def show_favorites(message: types.Message, page: int = 0):
    user = await users_collection.find_one({"user_id": message.from_user.id})
    faves = user.get("favorites", [])
    
    if not faves:
        await message.answer("Sizda hali saqlangan animelar yo'q. ❤️")
        return

    # Sahifalash: har bir sahifada 5 tadan anime
    items_per_page = 5
    total_pages = (len(faves) + items_per_page - 1) // items_per_page
    current_faves = faves[page * items_per_page : (page + 1) * items_per_page]

    kb = InlineKeyboardBuilder()
    for anime in current_faves:
        kb.row(types.InlineKeyboardButton(text=f"🎬 {anime['title']}", callback_data=f"info_{anime['mal_id']}"))
    
    # Sahifa raqamlari qatori
    nav_buttons = []
    for i in range(total_pages):
        label = f"[{i+1}]" if i == page else str(i+1)
        nav_buttons.append(types.InlineKeyboardButton(text=label, callback_data=f"fpage_{i}"))
    
    kb.row(*nav_buttons)
    
    text = f"❤️ <b>Sizning tanlanganlaringiz (Sahifa {page+1}/{total_pages}):</b>"
    if isinstance(message, types.CallbackQuery):
        await message.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="HTML")
    else:
        await message.answer(text, reply_markup=kb.as_markup(), parse_mode="HTML")

@dp.callback_query(F.data.startswith("fpage_"))
async def favorite_page_handler(callback: types.CallbackQuery):
    page = int(callback.data.split("_")[1])
    await show_favorites(callback, page)

# --- ANIME QIDIRUV VA SAQLASH ---
@dp.message(F.text)
async def main_handler(message: types.Message):
    if message.text.startswith("/") or message.text in ["🎲 Tasodifiy Anime", "🔥 Top Animelar", "❤️ Tanlanganlar", "🎭 Janrlar"]:
        return # Boshqa handlerlar ishlaydi

    user = await users_collection.find_one({"user_id": message.from_user.id})
    if not user or "adk" not in user:
        await message.answer("⚠️ Avval /start orqali ro'yxatdan o'ting!")
        return

    msg = await message.answer("Qidiryapman... 🔎")
    url = f"https://api.jikan.moe/v4/anime?q={message.text}&limit=1"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                res = await response.json()
                if res['data']:
                    anime = res['data'][0]
                    title = anime['title']
                    mal_id = anime['mal_id']
                    score = anime.get('score', 'N/A')
                    img = anime['images']['jpg']['large_image_url']
                    synopsis = await translate_to_uz(anime.get('synopsis', '')[:300])

                    caption = f"🎬 <b>Nomi:</b> {title}\n⭐ <b>Reyting:</b> {score}\n\n📝 <b>Annotatsiya:</b>\n{synopsis}..."
                    
                    kb = InlineKeyboardBuilder()
                    kb.row(types.InlineKeyboardButton(text="❤️ Saqlash", callback_data=f"save_{mal_id}"))
                    kb.add(types.InlineKeyboardButton(text="📢 Ulashish", switch_inline_query=title))
                    
                    await message.answer_photo(photo=img, caption=caption, parse_mode="HTML", reply_markup=kb.as_markup())
                    await msg.delete()
                else:
                    await msg.edit_text("Afsuski, topilmadi. ❌")

@dp.callback_query(F.data.startswith("save_"))
async def save_anime(callback: types.CallbackQuery):
    mal_id = int(callback.data.split("_")[1])
    anime_data = await get_anime_by_id(mal_id)
    
    if anime_data:
        await users_collection.update_one(
            {"user_id": callback.from_user.id},
            {"$addToSet": {"favorites": {"mal_id": mal_id, "title": anime_data['title']}}}
        )
        await callback.answer(f"✅ {anime_data['title']} saqlandi!", show_alert=True)

@dp.callback_query(F.data.startswith("info_"))
async def get_info_from_fave(callback: types.CallbackQuery):
    mal_id = int(callback.data.split("_")[1])
    anime = await get_anime_by_id(mal_id)
    if anime:
        # Xuddi qidiruvdagidek ma'lumot chiqarish
        title = anime['title']
        score = anime.get('score', 'N/A')
        img = anime['images']['jpg']['large_image_url']
        synopsis = await translate_to_uz(anime.get('synopsis', '')[:400])
        caption = f"🎬 <b>Nomi:</b> {title}\n⭐ <b>Reyting:</b> {score}\n\n📝 <b>Annotatsiya:</b>\n{synopsis}"
        await callback.message.answer_photo(photo=img, caption=caption, parse_mode="HTML")
        await callback.answer()

# --- ADMIN PANEL ---
@dp.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        print(f"ID xato: {message.from_user.id} != {ADMIN_ID}") # Logga yozadi
        return

    count = await users_collection.count_documents({})
    kb = InlineKeyboardBuilder()
    kb.add(types.InlineKeyboardButton(text="Xabar yuborish 📢", callback_data="admin_post"))
    await message.answer(f"📊 <b>Admin Panel</b>\n\nFoydalanuvchilar: {count} ta", parse_mode="HTML", reply_markup=kb.as_markup())

@dp.callback_query(F.data == "admin_post")
async def start_broadcast(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Xabarni yuboring:")
    await state.set_state(UserState.admin_broadcast)

@dp.message(UserState.admin_broadcast)
async def send_broadcast(message: types.Message, state: FSMContext):
    users = users_collection.find({})
    sent = 0
    async for user in users:
        try:
            await bot.send_message(user['user_id'], message.text)
            sent += 1
        except: pass
    await message.answer(f"Xabar {sent} kishiga yuborildi. ✅")
    await state.clear()

# --- ADK CREATION (OLDINGIDEK) ---
@dp.callback_query(F.data == "create_adk")
async def create_adk_cb(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Yangi ADK uchun 8 ta raqam yuboring:")
    await state.set_state(UserState.waiting_for_new_adk)

@dp.message(UserState.waiting_for_new_adk)
async def process_new_adk_logic(message: types.Message, state: FSMContext):
    if len(message.text) == 8 and message.text.isdigit():
        adk = f"AnICen/{message.text}/bot"
        if await users_collection.find_one({"adk": adk}):
            await message.answer("Bu ADK band! Boshqasini yozing:")
            return
        await users_collection.update_one({"user_id": message.from_user.id}, 
            {"$set": {"user_id": message.from_user.id, "adk": adk, "first_name": message.from_user.first_name, "favorites": []}}, upsert=True)
        await message.answer(f"✅ ADK yaratildi: <code>{adk}</code>", parse_mode="HTML", reply_markup=get_main_menu())
        await state.clear()
    else:
        await message.answer("Faqat 8 ta raqam!")

# (Eski ADK kiritish mantiqini ham 'have_adk' callback bilan qo'shish mumkin)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
