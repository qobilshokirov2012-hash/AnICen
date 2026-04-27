from aiogram import Router, F, types
from motor.motor_asyncio import AsyncIOMotorClient
from os import getenv

router = Router()
db = AsyncIOMotorClient(getenv("MONGO_URL"))['anicen_v2']
users_collection = db['users']

@router.message(F.text == "🌟 Sevimlilar")
async def favorites_handler(message: types.Message):
    user_data = await users_collection.find_one({"user_id": message.from_user.id})
    favs = user_data.get("favorites", [])
    
    if not favs:
        await message.answer("Sizning sevimlilar ro'yxatingiz bo'sh. 🧐")
    else:
        text = "🌟 <b>Sizning sevimlilaringiz:</b>\n\n"
        for i, anime in enumerate(favs, 1):
            text += f"{i}. {anime}\n"
        await message.answer(text, parse_mode="HTML")
        
