import os
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
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

# --- SIZ BERGAN PREMIUM EMOJI IDLARI ---
E_NOM = "5886473311637999700"          # Nom yozuvi uchun
E_SEARCH = "5888620056551625531"       # Nom qidiruv uchun
E_SIFAT = "5850392884817172292"        # Sifat (Reyting o'rnida ishlatsa bo'ladi)
E_TAG = "5890883384057533697"          # Teg (Annotatsiya uchun)
E_USER = "5938196735200333756"         # Foydalanuvchi
E_SHARE = "6039539366177541657"        # Ulashish
E_SILENT = "6039853100653612987"       # Ovozsiz

# Inglizcha matnni o'zbekchaga tarjima qilish
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

# Anime qidirish funksiyasi
async def search_anime(query):
    url = f"https://api.jikan.moe/v4/anime?q={query}&limit=1"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                if data['data']:
                    return data['data'][0]
            return None

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    
    # Foydalanuvchini bazaga tekshirish/qo'shish
    user = await users_collection.find_one({"user_id": user_id})
    user_emoji = f'<tg-emoji emoji-id="{E_USER}">👤</tg-emoji>'
    
    if not user:
        await users_collection.insert_one({
            "user_id": user_id, 
            "first_name": first_name,
            "username": message.from_user.username
        })
        text = f"{user_emoji} <b>Salom, {first_name}!</b>\n\nBotimizga xush kelibsiz! Anime nomini yozing va men sizga ma'lumot topib beraman."
    else:
        text = f"{user_emoji} <b>Qayta ko'rishganimizdan xursandman, {first_name}!</b>"

    await message.answer(text, parse_mode="HTML")

@dp.message(F.text)
async def handle_anime_search(message: types.Message):
    if message.text.startswith("/"): return

    search_emoji = f'<tg-emoji emoji-id="{E_SEARCH}">🔎</tg-emoji>'
    msg = await message.answer(f"Qidiryapman... {search_emoji}", parse_mode="HTML")
    
    anime = await search_anime(message.text)
    
    if anime:
        title = anime['title']
        score = anime.get('score', 'Noma’lum')
        image_url = anime['images']['jpg']['large_image_url']
        synopsis_en = anime.get('synopsis', 'Ma\'lumot yo\'q.')
        
        # O'zbekchaga tarjima (faqat dastlabki 500 harf)
        synopsis_uz = await translate_to_uz(synopsis_en[:500])
        
        # Emojilarni tayyorlash
        nom_emoji = f'<tg-emoji emoji-id="{E_NOM}">📝</tg-emoji>'
        sifat_emoji = f'<tg-emoji emoji-id="{E_SIFAT}">⭐</tg-emoji>'
        tag_emoji = f'<tg-emoji emoji-id="{E_TAG}">🏷</tg-emoji>'
        silent_emoji = f'<tg-emoji emoji-id="{E_SILENT}">🔇</tg-emoji>'
        
        caption = (
            f"{nom_emoji} <b>Nomi:</b> {title} {silent_emoji}\n"
            f"{sifat_emoji} <b>Reyting:</b> {score}\n\n"
            f"{tag_emoji} <b>Annotatsiya:</b>\n<i>{synopsis_uz}</i>"
        )
        
        # Ulashish tugmasini qo'shish
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
    
