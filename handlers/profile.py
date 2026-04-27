from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from motor.motor_asyncio import AsyncIOMotorClient
from os import getenv
from datetime import datetime

from config import EMOJIS
from keyboards import (
    profile_inline_keyboard,
    shop_inline_keyboard,
    back_to_shop_keyboard
)

router = Router()

client = AsyncIOMotorClient(getenv("MONGO_URL"))
db = client['anicen_v2']
users_collection = db['users']

@router.message(F.text == "👤 Profil")
@router.message(Command("ADK"))
async def profile_handler(message: types.Message):
    user_id = message.from_user.id
    user_data = await users_collection.find_one({"user_id": user_id})
    
    if not user_data:
        # Agar foydalanuvchi bazada bo'lmasa, vaqtinchalik yaratish yoki ogohlantirish
        await message.answer("Profil topilmadi. Iltimos, /start bosing.")
        return

    # Ma'lumotlarni xavfsiz olish
    first_name = user_data.get("first_name", message.from_user.first_name)
    ryo = user_data.get("ryo", 0)
    rank = user_data.get("rank", "Yangi")
    watched = user_data.get("watched_count", 0)
    fav_count = len(user_data.get("favorites", []))
    
    # SANA XATOSINI TO'G'RILASH
    join_date = user_data.get("join_date")
    if isinstance(join_date, datetime):
        reg_date = join_date.strftime("%d.%m.%Y")
    else:
        reg_date = datetime.now().strftime("%d.%m.%Y")

    profile_text = (
        f"<b>╔════ <tg-emoji emoji-id='{EMOJIS['profile2']}'>👤</tg-emoji> ANICEN PROFIL ════╗</b>\n\n"
        f"<tg-emoji emoji-id='{EMOJIS['id']}'>🆔</tg-emoji> <b>ID:</b> <code>{user_id}</code>\n"
        f"<tg-emoji emoji-id='{EMOJIS['profile']}'>👤</tg-emoji> <b>Foydalanuvchi:</b> {first_name}\n"
        f"<tg-emoji emoji-id='{EMOJIS['date']}'>📅</tg-emoji> <b>Sana:</b> {reg_date}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"<tg-emoji emoji-id='{EMOJIS['money']}'>💴</tg-emoji> <b>Ryo Balans:</b> <b>{ryo} Ryo</b>\n"
        f"<tg-emoji emoji-id='{EMOJIS['cup']}'>🏆</tg-emoji> <b>Daraja:</b> {rank}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"<tg-emoji emoji-id='{EMOJIS['favorite']}'>🌟</tg-emoji> <b>Sevimlilar:</b> {fav_count} ta\n"
        f"<tg-emoji emoji-id='{EMOJIS['watched']}'>🎬</tg-emoji> <b>Ko‘rilgan:</b> {watched} ta\n"
        f"╚══════════════════════╝"
    )
    
    await message.answer(profile_text, reply_markup=profile_inline_keyboard(), parse_mode=ParseMode.HTML)

# Shop va boshqa handlerlar o'zgarishsiz qoladi...
