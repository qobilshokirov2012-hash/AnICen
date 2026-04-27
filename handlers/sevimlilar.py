from aiogram import Router, F, types
from aiogram.enums import ParseMode
from motor.motor_asyncio import AsyncIOMotorClient
from os import getenv

# config.py va keyboards.py dan kerakli narsalarni import qilamiz
from config import EMOJIS
from keyboards import (
    favorites_inline_keyboard, 
    back_to_fav_keyboard
)

router = Router()

# Ma'lumotlar bazasi ulanishi
client = AsyncIOMotorClient(getenv("MONGO_URL"))
db = client['anicen_v2']
users_collection = db['users']

# 1. ASOSIY SEVIMLILAR MENYUSI (REPLY TUGMA BOSILGANDA)
@router.message(F.text == "🌟 Sevimlilar")
async def favorites_main_handler(message: types.Message):
    user_id = message.from_user.id
    user_data = await users_collection.find_one({"user_id": user_id})
    
    if not user_data:
        await message.answer("Profil topilmadi. Iltimos, /start bosing.")
        return
        
    favs = user_data.get("favorites", [])
    
    if not favs:
        fav_list = (
            f"<i>Hozircha ro'yxatingiz bo'sh. \n"
            f"Animelarga kirib <tg-emoji emoji-id='{EMOJIS['favorite']}'>🌟</tg-emoji> tugmasini bosing!</i>"
        )
    else:
        fav_list = "<b>Siz yoqtirgan animelar:</b>\n\n"
        for i, name in enumerate(favs[:10], 1): # Dastlabki 10 tasini ko'rsatish
            fav_list += f"<b>{i}.</b> {name}\n"
            
    text = (
        f"<tg-emoji emoji-id='{EMOJIS['favorite']}'>🌟</tg-emoji> <b>Sevimlilaringiz</b>\n\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"{fav_list}\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"<tg-emoji emoji-id='{EMOJIS['loading']}'>🔄</tg-emoji> <i>Boshqarish uchun tugmalardan foydalaning:</i>"
    )
    
    await message.answer(text, reply_markup=favorites_inline_keyboard(), parse_mode=ParseMode.HTML)

# 2. SEVIMLILAR HAQIDA (INLINE TUGMA)
@router.callback_query(F.data == "fav_about")
async def fav_about_handler(callback: types.CallbackQuery):
    text = (
        f"<tg-emoji emoji-id='{EMOJIS['question']}'>❓</tg-emoji> <b>Sevimlilar bo‘limi haqida</b>\n\n"
        f"Ushbu bo‘lim sizning shaxsiy kutubxonangiz hisoblanadi. "
        f"Har bir anime sahifasidagi <tg-emoji emoji-id='{EMOJIS['save']}'>💾</tg-emoji> tugmasini "
        f"bosish orqali ularni shu yerga yig'ib borishingiz mumkin.\n\n"
        f"<tg-emoji emoji-id='{EMOJIS['tag']}'>🏷</tg-emoji> <b>Maksimal sig‘im:</b> 50 ta anime"
    )
    await callback.message.edit_text(text, reply_markup=back_to_fav_keyboard(), parse_mode=ParseMode.HTML)

# 3. OXIRGI QO'SHILGANLAR (INLINE TUGMA)
@router.callback_query(F.data == "fav_recent")
async def fav_recent_handler(callback: types.CallbackQuery):
    user_data = await users_collection.find_one({"user_id": callback.from_user.id})
    favs = user_data.get("favorites", [])
    
    if not favs:
        recent_text = "Hali anime qo'shilmagan."
    else:
        # Oxirgi 5 tasini teskari tartibda (eng yangilarini) olish
        recent = favs[::-1][:5]
        recent_text = ""
        for name in recent:
            recent_text += f"<tg-emoji emoji-id='{EMOJIS['new']}'>🆕</tg-emoji> {name}\n"
        
    text = (
        f"<tg-emoji emoji-id='{EMOJIS['continue']}'>🕒</tg-emoji> <b>Oxirgi qo‘shilganlar:</b>\n\n"
        f"{recent_text}\n"
        f"━━━━━━━━━━━━━━━"
    )
    await callback.message.edit_text(text, reply_markup=back_to_fav_keyboard(), parse_mode=ParseMode.HTML)

# 4. ORQAGA QAYTISH (SEVIMLILAR ASOSIY MENYUSIGA)
@router.callback_query(F.data == "back_to_fav")
async def back_to_fav_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user_data = await users_collection.find_one({"user_id": user_id})
    favs = user_data.get("favorites", [])
    
    if not favs:
        fav_list = "Ro'yxat bo'sh."
    else:
        fav_list = "<b>Siz yoqtirgan animelar:</b>\n\n"
        for i, name in enumerate(favs[:10], 1):
            fav_list += f"<b>{i}.</b> {name}\n"
            
    text = (
        f"<tg-emoji emoji-id='{EMOJIS['favorite']}'>🌟</tg-emoji> <b>Sevimlilaringiz</b>\n\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"{fav_list}\n\n"
        f"━━━━━━━━━━━━━━━"
    )
    await callback.message.edit_text(text, reply_markup=favorites_inline_keyboard(), parse_mode=ParseMode.HTML)

# 5. O'CHIRISH (AGAR KEYBOARDS'DA SHUNDAY TUGMA BO'LSA)
@router.callback_query(F.data == "clear_favorites")
async def clear_fav_handler(callback: types.CallbackQuery):
    await users_collection.update_one(
        {"user_id": callback.from_user.id},
        {"$set": {"favorites": []}}
    )
    await callback.answer("Barcha sevimlilar o'chirildi!", show_alert=True)
    await back_to_fav_callback(callback)
    
