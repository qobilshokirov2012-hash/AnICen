import os
import re
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from database import *
from keyboards import main_menu

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# ================= START =================
@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    user = get_user(msg.from_user.id)

    if not user:
        create_user({
            "user_id": msg.from_user.id,
            "name": msg.from_user.first_name,
            "username": msg.from_user.username,
            "adk": None,
            "favorites": [],
            "created_at": msg.date
        })

        text = f"""Salom, {msg.from_user.first_name}! 👋

Dunyodagi eng qiziqarli animelar olamiga xush kelibsiz! Bu yerda siz:

🔍 Izlash — Sevimli animengizni topishingiz  
⭐ Tanlanganlar — O'zingizga yoqqanlarini saqlashingiz  
🎲 Tasodifiy — Nima ko'rishni bilmayotgan bo'lsangiz, tavsiyalar olishingiz mumkin  

Pastdagi tugmalardan birini tanlang:
"""
    else:
        adk = user.get("adk") or "yo‘q"

        text = f"""Sizni yana koʻrganimizdan xursandmiz! {msg.from_user.first_name} 👋

🆔 ID: {msg.from_user.id}  
🔑 ADK: {adk}

Bugun nima koʻramiz? Tanlanganlar roʻyxatingizda yangi qismlar yoki siz kutgan animelar chiqib qolgan boʻlishi mumkin!

Davom etish uchun menyudan kerakli boʻlimni tanlang:
"""

    await msg.answer(text, reply_markup=main_menu())

# ================= SEARCH =================
@dp.callback_query_handler(lambda c: c.data == "search")
async def search_btn(call: types.CallbackQuery):
    await call.message.answer("🔍 Anime nomini yozing:")

@dp.message_handler()
async def search(msg: types.Message):
    query = msg.text

    url = f"https://api.jikan.moe/v4/anime?q={query}&limit=1"
    res = requests.get(url).json()

    if not res["data"]:
        await msg.answer("❌ Anime topilmadi")
        return

    anime = res["data"][0]

    caption = f"""🎬 {anime['title']}
⭐ {anime['score']}
📅 {anime.get('year', 'Nomaʼlum')}

📖 {anime['synopsis'][:200]}...
"""

    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("⭐ Saqlash", callback_data=f"fav_{anime['title']}"))

    await bot.send_photo(
        msg.chat.id,
        anime["images"]["jpg"]["image_url"],
        caption=caption,
        reply_markup=kb
    )

# ================= FAVORITES =================
@dp.callback_query_handler(lambda c: c.data.startswith("fav_"))
async def add_fav(call: types.CallbackQuery):
    title = call.data.split("_", 1)[1]

    add_favorite(call.from_user.id, {"title": title})

    await call.answer("⭐ Saqlandi!")

@dp.callback_query_handler(lambda c: c.data == "favorites")
async def show_fav(call: types.CallbackQuery):
    favs = get_favorites(call.from_user.id)

    if not favs:
        await call.message.answer("❌ Tanlanganlar bo‘sh")
        return

    text = "⭐ Tanlanganlar:\n\n"
    for f in favs[:5]:
        text += f"• {f['title']}\n"

    await call.message.answer(text)

# ================= ADK =================
user_states = {}

@dp.callback_query_handler(lambda c: c.data == "create_adk")
async def create_adk(call: types.CallbackQuery):
    user_states[call.from_user.id] = "waiting_adk"
    await call.message.answer("8 ta raqam kiriting:")

@dp.message_handler(lambda msg: user_states.get(msg.from_user.id) == "waiting_adk")
async def save_adk(msg: types.Message):
    code = msg.text

    if not re.fullmatch(r"\d{8}", code):
        await msg.answer("❌ Faqat 8 ta raqam!")
        return

    adk = f"AnICen/{code}/bot"

    # unique check
    if users.find_one({"adk": adk}):
        await msg.answer("❌ Bu ADK band!")
        return

    update_user(msg.from_user.id, {"adk": adk})
    user_states.pop(msg.from_user.id)

    await msg.answer(f"✅ ADK yaratildi:\n{adk}")

@dp.callback_query_handler(lambda c: c.data == "have_adk")
async def have_adk(call: types.CallbackQuery):
    user_states[call.from_user.id] = "check_adk"
    await call.message.answer("ADK kiriting:")

@dp.message_handler(lambda msg: user_states.get(msg.from_user.id) == "check_adk")
async def check_adk(msg: types.Message):
    adk = msg.text

    if not users.find_one({"adk": adk}):
        await msg.answer("❌ ADK topilmadi")
        return

    update_user(msg.from_user.id, {"adk": adk})
    user_states.pop(msg.from_user.id)

    await msg.answer("✅ ADK tasdiqlandi")

# ================= ADMIN UPLOAD =================
@dp.message_handler(commands=['upload'])
async def upload(msg: types.Message):
    if msg.from_user.id != ADMIN_ID:
        return

    # oddiy test
    title = "Naruto"

    users_list = find_users_with_favorite(title)

    for u in users_list:
        try:
            await bot.send_message(
                u["user_id"],
                f"🚀 Siz kutgan \"{title}\"ning yangi qismi yuklandi!"
            )
        except:
            pass

# ================= RUN =================
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
