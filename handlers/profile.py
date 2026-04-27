from aiogram import Router, F, types
from aiogram.enums import ParseMode
from motor.motor_asyncio import AsyncIOMotorClient
from os import getenv
from config import EMOJIS
from keyboards import (
    profile_inline_keyboard,
    shop_inline_keyboard,
    back_to_shop_keyboard
)

router = Router()

# DB ulanishi
client = AsyncIOMotorClient(getenv("MONGO_URL"))
db = client['anicen_v2']
users_collection = db['users']

# PROFIL VA /ADK BUYRUG'I
@router.message(F.text == "👤 Profil")
@router.message(F.text == "/ADK")
async def profile_handler(message: types.Message):
    user_data = await users_collection.find_one({"user_id": message.from_user.id})
    if not user_data: return
    
    reg_date = user_data.get("join_date").strftime("%d.%m.%Y") if user_data.get("join_date") else "Noma'lum"
    
    text = (
        f"<b>AnICen | {user_data.get('first_name')}</b>\n"
        f"<tg-emoji emoji-id='{EMOJIS['profile']}'>👤</tg-emoji> Profil\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🆔 ID: <code>{message.from_user.id}</code>\n"
        f"📅 Ro‘yxatdan o‘tgan: {reg_date}\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"<tg-emoji emoji-id='{EMOJIS['star']}'>🌟</tg-emoji> Sevimlilar: {len(user_data.get('favorites', []))}\n"
        f"<tg-emoji emoji-id='{EMOJIS['watched']}'>🎬</tg-emoji> Ko‘rilgan: {user_data.get('watched_count', 0)}\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"<tg-emoji emoji-id='{EMOJIS['rank']}'>🧠</tg-emoji> Daraja: {user_data.get('rank')}\n"
        f"<tg-emoji emoji-id='{EMOJIS['ryo']}'>💴</tg-emoji> Ryo: {user_data.get('ryo', 0)}\n"
    )
    await message.answer(text, reply_markup=profile_inline_keyboard(), parse_mode=ParseMode.HTML)

# DO'KON MENYUSI
@router.callback_query(F.data == "open_shop")
@router.message(F.text == "🛒 Do‘kon")
async def shop_handler(event: types.Message | types.CallbackQuery):
    user_id = event.from_user.id
    user_data = await users_collection.find_one({"user_id": user_id})
    ryo = user_data.get("ryo", 0)
    
    text = (
        f"🛒 <b>AnICen Do‘koni</b>\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"💴 Sizning Ryo: <b>{ryo}</b>\n\n"
        f"⚔️ Kakashi — 567 Ryo\n"
        f"🌸 Sakura — 600 Ryo\n"
        f"🗡 Sasuke — 693 Ryo\n"
        f"🍥 Naruto — 787 Ryo\n"
    )
    if isinstance(event, types.Message):
        await event.answer(text, reply_markup=shop_inline_keyboard(), parse_mode=ParseMode.HTML)
    else:
        await event.message.edit_text(text, reply_markup=shop_inline_keyboard(), parse_mode=ParseMode.HTML)

# RANK SOTIB OLISH (ALERT BILAN)
@router.callback_query(F.data.startswith("buy_rank_"))
async def buy_rank_handler(callback: types.CallbackQuery):
    rank_key = callback.data.split("_")[-1]
    prices = {"kakashi": 567, "sakura": 600, "sasuke": 693, "naruto": 787}
    price = prices.get(rank_key)
    
    user_data = await users_collection.find_one({"user_id": callback.from_user.id})
    if user_data.get("ryo", 0) < price:
        await callback.answer("❌ Ryoyingiz yetarli emas!", show_alert=True)
    else:
        await users_collection.update_one(
            {"user_id": callback.from_user.id},
            {"$inc": {"ryo": -price}, "$set": {"rank": rank_key.capitalize()}}
        )
        await callback.answer(f"✅ {rank_key.capitalize()} darajasi olindi!", show_alert=True)
      
