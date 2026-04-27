from aiogram import Router, F, types
from aiogram.enums import ParseMode
from motor.motor_asyncio import AsyncIOMotorClient
from os import getenv
from config import EMOJIS
from keyboards import (
    favorites_inline_keyboard, 
    back_to_fav_keyboard
)

# Router yaratamiz (bu Dispatcher o'rniga ishlaydi)
router = Router()

# Ma'lumotlar bazasi
client = AsyncIOMotorClient(getenv("MONGO_URL"))
db = client['anicen_v2']
users_collection = db['users']

# 1. ASOSIY SEVIMLILAR MENYUSI (REPLY TUGMA)
@router.message(F.text == "🌟 Sevimlilar")
async def favorites_main_handler(message: types.Message):
    user_data = await users_collection.find_one({"user_id": message.from_user.id})
    favs = user_data.get("favorites", []) if user_data else []
    
    if not favs:
        fav_list = "Hozircha ro'yxatingiz bo'sh. \nAnimelarga kirib 🌟 tugmasini bosing!"
    else:
        fav_list = "Siz yoqtirgan animelar:\n\n"
        for i, name in enumerate(favs[:10], 1):
            fav_list += f"{i}. <b>{name}</b>\n"
            
    text = (
        f"<tg-emoji emoji-id='{EMOJIS['star']}'>🌟</tg-emoji> <b>Sevimlilaringiz</b>\n\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"{fav_list}\n\n"
        f"━━━━━━━━━━━━━━━"
    )
    await message.answer(text, reply_markup=favorites_inline_keyboard(), parse_mode=ParseMode.HTML)

# 2. SEVIMLILAR HAQIDA (INLINE)
@router.callback_query(F.data == "fav_about")
async def fav_about_handler(callback: types.CallbackQuery):
    text = (
        f"<tg-emoji emoji-id='{EMOJIS['info']}'>ℹ️</tg-emoji> <b>Sevimlilar haqida</b>\n\n"
        f"Bu bo'limda siz saqlab qo'ygan animelar ro'yxati shakllanadi. "
        f"Har bir anime sahifasidagi 🌟 tugmasi orqali ularni shu yerga yig'ishingiz mumkin."
    )
    await callback.message.edit_text(text, reply_markup=back_to_fav_keyboard(), parse_mode=ParseMode.HTML)

# 3. OXIRGI QO'SHILGANLAR (INLINE)
@router.callback_query(F.data == "fav_recent")
async def fav_recent_handler(callback: types.CallbackQuery):
    user_data = await users_collection.find_one({"user_id": callback.from_user.id})
    favs = user_data.get("favorites", []) if user_data else []
    
    recent_list = "\n".join([f"🔹 {name}" for name in favs[::-1][:5]]) if favs else "Hali anime qo'shilmagan."
    
    text = (
        f"<tg-emoji emoji-id='{EMOJIS['recent']}'>🕒</tg-emoji> <b>Oxirgi qo'shilganlar:</b>\n\n"
        f"{recent_list}"
    )
    await callback.message.edit_text(text, reply_markup=back_to_fav_keyboard(), parse_mode=ParseMode.HTML)

# 4. ORQAGA QAYTISH
@router.callback_query(F.data == "back_to_fav")
async def back_to_fav_callback(callback: types.CallbackQuery):
    user_data = await users_collection.find_one({"user_id": callback.from_user.id})
    favs = user_data.get("favorites", []) if user_data else []
    
    fav_list = "\n".join([f"{i+1}. {name}" for i, name in enumerate(favs[:10])]) if favs else "Bo'sh"
    
    text = (
        f"<tg-emoji emoji-id='{EMOJIS['star']}'>🌟</tg-emoji> <b>Sevimlilaringiz:</b>\n\n"
        f"{fav_list}"
    )
    await callback.message.edit_text(text, reply_markup=favorites_inline_keyboard(), parse_mode=ParseMode.HTML)
  
