import os
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from motor.motor_asyncio import AsyncIOMotorClient

TOKEN = os.getenv("BOT_TOKEN")
MONGO_URL = os.getenv("MONGO_URL")

bot = Bot(token=TOKEN)
dp = Dispatcher()

client = AsyncIOMotorClient(MONGO_URL)
db = client.anime_bot_db
users_collection = db.users

# Siz bergan Premium Emoji IDlaridan namunalar
EMOJI_STAR = "6039646800489486634"
EMOJI_FIRE = "5890883384057533697"
EMOJI_DIAMOND = "6039853100653612987"
EMOJI_SEARCH = "6033125983572201397"

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
    
    user = await users_collection.find_one({"user_id": user_id})
    
    # Premium emoji bilan salomlashish (HTML formatda)
    welcome_emoji = f'<tg-emoji emoji-id="{EMOJI_STAR}">✨</tg-emoji>'
    
    if not user:
        await users_collection.insert_one({
            "user_id": user_id,
            "first_name": first_name,
            "username": message.from_user.username
        })
        text = f"<b>Salom, {first_name}!</b> {welcome_emoji}\n\n<b>Sizning ID:</b> <code>{user_id}</code>\nAnime nomini yuboring!"
    else:
        text = f"<b>Qayta ko'rishganimizdan xursandman!</b> {welcome_emoji}\nAnime nomini yuboring!"

    await message.answer(text, parse_mode="HTML")

@dp.message(F.text)
async def handle_anime_search(message: types.Message):
    search_emoji = f'<tg-emoji emoji-id="{EMOJI_SEARCH}">🔎</tg-emoji>'
    msg = await message.answer(f"Qidiryapman... {search_emoji}", parse_mode="HTML")
    
    anime = await search_anime(message.text)
    
    if anime:
        title = anime['title']
        score = anime.get('score', 'Noma’lum')
        image_url = anime['images']['jpg']['large_image_url']
        
        # Sarlavhaga brilliant emoji qo'shamiz
        diamond = f'<tg-emoji emoji-id="{EMOJI_DIAMOND}">💎</tg-emoji>'
        fire = f'<tg-emoji emoji-id="{EMOJI_FIRE}">🔥</tg-emoji>'
        
        caption = (
            f"🎬 <b>Nomi:</b> {title} {diamond}\n"
            f"⭐ <b>Reyting:</b> {score} {fire}\n\n"
            f"📝 <b>Annotatsiya:</b> {anime.get('synopsis', '...')[:200]}..."
        )
        
        await message.answer_photo(photo=image_url, caption=caption, parse_mode="HTML")
        await msg.delete()
    else:
        await msg.edit_text("Topilmadi ❌")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
