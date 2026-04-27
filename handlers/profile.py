from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from motor.motor_asyncio import AsyncIOMotorClient
from os import getenv
from datetime import datetime
from config import EMOJIS
from keyboards import profile_inline_keyboard

router = Router()
db = AsyncIOMotorClient(getenv("MONGO_URL"))['anicen_v2']
users_collection = db['users']

@router.message(F.text == "👤 Profil")
@router.message(Command("ADK"))
async def profile_handler(message: types.Message):
    user_id = message.from_user.id
    user_data = await users_collection.find_one({"user_id": user_id})
    
    if not user_data:
        await message.answer("Profil topilmadi. /start bosing.")
        return

    # Ma'lumotlarni xavfsiz olish (None bo'lsa default qiymat beriladi)
    ryo = user_data.get("ryo", 0)
    rank = user_data.get("rank", "Yangi")
    
    # Sana tekshiruvi (Crash oldini olish)
    join_date = user_data.get("join_date")
    reg_date = join_date.strftime("%d.%m.%Y") if isinstance(join_date, datetime) else "Noma'lum"

    text = (
        f"<b>👤 PROFIL</b>\n\n"
        f"🆔 ID: <code>{user_id}</code>\n"
        f"📅 Sana: {reg_date}\n"
        f"💴 Balans: {ryo} Ryo\n"
        f"🏆 Daraja: {rank}"
    )
    await message.answer(text, reply_markup=profile_inline_keyboard(), parse_mode=ParseMode.HTML)
    
