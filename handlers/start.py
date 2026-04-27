from aiogram import Router, F, types
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from motor.motor_asyncio import AsyncIOMotorClient
from os import getenv
from datetime import datetime, timezone

# config.py va keyboards.py dan importlar
from config import EMOJIS
from keyboards import (
    language_selection_keyboard,
    main_reply_keyboard
)

router = Router()

# Ma'lumotlar bazasi ulanishi
client = AsyncIOMotorClient(getenv("MONGO_URL"))
db = client['anicen_v2']
users_collection = db['users']

# 1. START BUYRUG'I
@router.message(CommandStart())
async def start_command(message: types.Message):
    user_id = message.from_user.id
    user_data = await users_collection.find_one({"user_id": user_id})
    
    # Agar foydalanuvchi bazada bo'lmasa - Til tanlashni ko'rsatamiz
    if not user_data:
        text = (
            f"<tg-emoji emoji-id='{EMOJIS['new']}'>🆕</tg-emoji> <b>Xush kelibsiz! / Welcome!</b>\n\n"
            f"AnICen botiga xush kelibsiz. Davom etish uchun tilni tanlang:\n"
            f"Please select your language to continue:\n\n"
            f"━━━━━━━━━━━━━━━\n"
            f"<tg-emoji emoji-id='{EMOJIS['jap']}'>🇯🇵</tg-emoji> <i>O'zbekistonning eng katta anime portali!</i>"
        )
        await message.answer(text, reply_markup=language_selection_keyboard(), parse_mode=ParseMode.HTML)
    else:
        # Agar foydalanuvchi allaqachon bo'lsa - Asosiy menyu
        first_name = user_data.get("first_name", message.from_user.first_name)
        text = (
            f"<tg-emoji emoji-id='{EMOJIS['gojo']}'>👓</tg-emoji> <b>Salom, {first_name}!</b>\n\n"
            f"Sizni yana ko'rganimizdan xursandmiz! Bugun qanday anime ko'ramiz?\n\n"
            f"<tg-emoji emoji-id='{EMOJIS['top']}'>🔝</tg-emoji> <b>Trenddagi animelar yangilandi!</b>"
        )
        await message.answer(text, reply_markup=main_reply_keyboard(), parse_mode=ParseMode.HTML)

# 2. TILNI SAQLASH MANTIQI
@router.callback_query(F.data.startswith("set_lang_"))
async def save_language_callback(callback: types.CallbackQuery):
    lang_code = callback.data.split("_")[-1]
    user_id = callback.from_user.id
    
    # Bazaga foydalanuvchini qo'shish yoki yangilash
    await users_collection.update_one(
        {"user_id": user_id},
        {"$set": {
            "lang": lang_code,
            "first_name": callback.from_user.first_name,
            "ryo": 16, # Bonus start ryo
            "rank": "Yangi",
            "watched_count": 0,
            "favorites": [],
            "notify": True,
            "daily_reminder": True,
            "join_date": datetime.now(timezone.utc)
        }},
        upsert=True
    )
    
    # Muvaffaqiyatli xabar
    await callback.answer(f"✅ Til tanlandi: {lang_code.upper()}")
    await callback.message.delete()
    
    success_text = (
        f"<tg-emoji emoji-id='{EMOJIS['correct']}'>✅</tg-emoji> <b>Muvaffaqiyatli sozlandi!</b>\n\n"
        f"Sizga <b>16 Ryo</b> start bonusi berildi <tg-emoji emoji-id='{EMOJIS['money']}'>💴</tg-emoji>\n\n"
        f"Keling, sarguzashtni boshlaymiz!"
    )
    await callback.message.answer(success_text, reply_markup=main_reply_keyboard(), parse_mode=ParseMode.HTML)
  
