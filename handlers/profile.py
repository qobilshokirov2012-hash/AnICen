from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from motor.motor_asyncio import AsyncIOMotorClient
from os import getenv
from datetime import datetime

# config.py va keyboards.py dan importlar
from config import EMOJIS
from keyboards import (
    profile_inline_keyboard,
    shop_inline_keyboard,
    back_to_shop_keyboard
)

# Router ob'ektini yaratish (BU JUDA MUHIM)
router = Router()

# Ma'lumotlar bazasi ulanishi
client = AsyncIOMotorClient(getenv("MONGO_URL"))
db = client['anicen_v2']
users_collection = db['users']

# 1. PROFIL HANDLERI (/ADK VA TUGMA)
@router.message(F.text == "👤 Profil")
@router.message(Command("ADK"))
async def profile_handler(message: types.Message):
    user_id = message.from_user.id
    user_data = await users_collection.find_one({"user_id": user_id})
    
    if not user_data:
        await message.answer("Profil topilmadi. /start bosing.")
        return

    first_name = user_data.get("first_name", message.from_user.first_name)
    # Sanani formatlash
    join_date = user_data.get("join_date")
    reg_date = join_date.strftime("%d.%m.%Y") if join_date else "Noma'lum"
    
    ryo = user_data.get("ryo", 0)
    rank = user_data.get("rank", "Yangi")
    watched = user_data.get("watched_count", 0)
    fav_count = len(user_data.get("favorites", []))

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

# 2. DO'KON MENYUSI
@router.callback_query(F.data == "open_shop")
@router.message(F.text == "🛒 Do‘kon")
async def shop_handler(event: types.Message | types.CallbackQuery):
    user_id = event.from_user.id
    user_data = await users_collection.find_one({"user_id": user_id})
    ryo = user_data.get("ryo", 0)
    
    shop_text = (
        f"<tg-emoji emoji-id='{EMOJIS['money']}'>💴</tg-emoji> <b>ANICEN DO‘KON</b>\n\n"
        f"Sizning balansingiz: <b>{ryo} Ryo</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"<tg-emoji emoji-id='{EMOJIS['kakashi']}'>🥷</tg-emoji> <b>Kakashi Rank</b> — 567 Ryo\n"
        f"<tg-emoji emoji-id='{EMOJIS['gojo']}'>👓</tg-emoji> <b>Satoru Gojo Rank</b> — 600 Ryo\n"
        f"<tg-emoji emoji-id='{EMOJIS['naruto']}'>🍥</tg-emoji> <b>Naruto Rank</b> — 787 Ryo\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"<i>Xarid qilish uchun quyidagi tugmalarni bosing:</i>"
    )

    if isinstance(event, types.Message):
        await event.answer(shop_text, reply_markup=shop_inline_keyboard(), parse_mode=ParseMode.HTML)
    else:
        await event.message.edit_text(shop_text, reply_markup=shop_inline_keyboard(), parse_mode=ParseMode.HTML)

# 3. RANK SOTIB OLISH MANTIQI
@router.callback_query(F.data.startswith("buy_rank_"))
async def buy_rank_process(callback: types.CallbackQuery):
    rank_key = callback.data.split("_")[-1]
    prices = {"kakashi": 567, "gojo": 600, "naruto": 787}
    price = prices.get(rank_key)
    
    user_data = await users_collection.find_one({"user_id": callback.from_user.id})
    current_ryo = user_data.get("ryo", 0)
    
    if current_ryo < price:
        await callback.answer(f"❌ Mablag‘ yetarli emas! Sizga yana {price - current_ryo} Ryo kerak.", show_alert=True)
    else:
        new_rank_name = rank_key.capitalize()
        await users_collection.update_one(
            {"user_id": callback.from_user.id},
            {
                "$inc": {"ryo": -price},
                "$set": {"rank": new_rank_name}
            }
        )
        await callback.answer(f"🎉 Tabriklaymiz! Siz {new_rank_name} darajasini sotib oldingiz!", show_alert=True)
        await shop_handler(callback)

# 4. RYO HAQIDA MA'LUMOT
@router.callback_query(F.data == "about_ryo")
async def about_ryo_handler(callback: types.CallbackQuery):
    text = (
        f"<tg-emoji emoji-id='{EMOJIS['money']}'>💴</tg-emoji> <b>Ryo tizimi haqida</b>\n\n"
        f"Ryo — bu bot ichidagi valyuta bo‘lib, u orqali maxsus statuslar va imkoniyatlarni sotib olish mumkin.\n\n"
        f"<tg-emoji emoji-id='{EMOJIS['add']}'>➕</tg-emoji> <b>Qanday yig‘iladi?</b>\n"
        f"• Har bir anime ko‘rilganda: +10 Ryo\n"
        f"• Kunlik kirish uchun: +5 Ryo\n"
        f"• Taklif qilingan do'st uchun: +26 Ryo"
    )
    await callback.message.edit_text(text, reply_markup=back_to_shop_keyboard(), parse_mode=ParseMode.HTML)
    
