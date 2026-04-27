import asyncio
import logging
import random
from datetime import datetime, timezone
from os import getenv

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode
from motor.motor_asyncio import AsyncIOMotorClient

# Keyboards faylingizdan barcha kerakli funksiyalarni import qilamiz
from keyboards import (
    main_menu_keyboard, 
    main_reply_keyboard, 
    back_to_main_keyboard,
    favorites_inline_keyboard,
    back_to_fav_keyboard,  # Mana shu yangi qo'shildi
    anime_item_keyboard,
    profile_inline_keyboard,
    spend_points_inline_keyboard
)

from config import EMOJIS

# --- KONFIGURATSIYA ---
BOT_TOKEN = getenv("BOT_TOKEN")
MONGO_URL = getenv("MONGO_URL")

client = AsyncIOMotorClient(MONGO_URL)
db = client['anicen_v2']
users_collection = db['users']

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- START HANDLER ---
@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    try:
        user_id = message.from_user.id
        first_name = message.from_user.first_name
        
        user_data = await users_collection.find_one({"user_id": user_id})
        if not user_data:
            await users_collection.insert_one({
                "user_id": user_id,
                "first_name": first_name,
                "points": 50,
                "favorites": [],
                "join_date": datetime.now(timezone.utc)
            })
            
        welcome_text = (
            f"<b>╔═══ANICEN═══╗</b>\n"
            f"<b>╚═══════════╝</b>\n\n"
            f"<tg-emoji emoji-id='{EMOJIS['welcome']}'>👋</tg-emoji> Salom, <b>{first_name}</b>!\n\n"
            f"Siz bu yerda:\n"
            f"<tg-emoji emoji-id='{EMOJIS['profile']}'>👤</tg-emoji> Profil ochasiz\n"
            f"<tg-emoji emoji-id='{EMOJIS['search']}'>🔍</tg-emoji> Anime qidirasiz\n"
            f"<tg-emoji emoji-id='{EMOJIS['episodes']}'>🎬</tg-emoji> Epizodlarni tomosha qilasiz\n"
            f"<tg-emoji emoji-id='{EMOJIS['favorite']}'>🌟</tg-emoji> Sevimlilarni saqlaysiz\n\n"
            f"━━━━━━━━━━━━━━━\n"
            f"<tg-emoji emoji-id='{EMOJIS['trend']}'>🔥</tg-emoji> Trend animelar sizni kutmoqda!\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"<tg-emoji emoji-id='{EMOJIS['start']}'>⚡</tg-emoji> Boshlash uchun tugmani tanlang:"
        )
        await message.answer(welcome_text, reply_markup=main_reply_keyboard(), parse_mode=ParseMode.HTML)
    except Exception as e:
        logging.error(f"Start xatosi: {e}")

# --- PROFIL BO'LIMI ---
# bot.py dagi profil qismini shunday yangilang:

@dp.message(F.text == "👤 Profil")
async def profile_handler(message: types.Message):
    user_data = await users_collection.find_one({"user_id": message.from_user.id})
    points = user_data.get("points", 0) if user_data else 0
    
    text = (
        f"<tg-emoji emoji-id='{EMOJIS['profile']}'>👤</tg-emoji> <b>PROFILINGIZ</b>\n\n"
        f"💰 Ballaringiz: <b>{points} ball</b>\n\n"
        f"<i>Ballaringiz orqali botdagi turli xizmatlarni sotib olishingiz mumkin!</i>"
    )
    # Mana shu yerda profile_inline_keyboard() ni ulaymiz
    await message.answer(text, reply_markup=profile_inline_keyboard(), parse_mode=ParseMode.HTML)

# Ballarni sarflash tugmasi bosilganda
@dp.callback_query(F.data == "spend_points")
async def spend_points_handler(callback: types.CallbackQuery):
    text = (
        "🪙 <b>Ballarni sarflash bo'limi</b>\n\n"
        "O'zingizga kerakli xizmatni tanlang:"
    )
    await callback.message.edit_text(text, reply_markup=spend_points_inline_keyboard(), parse_mode=ParseMode.HTML)
    
# --- SEVIMLILAR BO'LIMI ---
@dp.message(F.text == "🌟 Sevimlilar")
async def favorites_handler(message: types.Message):
    user_id = message.from_user.id
    user_data = await users_collection.find_one({"user_id": user_id})
    favs = user_data.get("favorites", [])
    
    if not favs:
        fav_list = "Hozircha ro'yxat bo'sh."
    else:
        fav_list = "\n".join([f"{i+1}. {name}" for i, name in enumerate(favs[:10])])

    text = (
        f"<tg-emoji emoji-id='5258259534857645678'>🌟</tg-emoji> <b>Sizning sevimli animelaringiz:</b>\n\n"
        f"{fav_list}\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"<i>Qolgan ma'lumotlar uchun 'Haqida? ↓' tugmasini bosing.</i>"
    )
    await message.answer(text, reply_markup=favorites_inline_keyboard(), parse_mode=ParseMode.HTML)

# --- "HAQIDA? ↓" TUGMASI (Matn shu yerga ko'chirildi) ---
@dp.callback_query(F.data == "fav_about")
async def fav_about_handler(callback: types.CallbackQuery):
    about_text = (
        f"<tg-emoji emoji-id='5352743837502545676'>🌟</tg-emoji> <b>Sevimlilar (Favorites)</b>\n"
        f"<tg-emoji emoji-id='5442875573045045415'>📄</tg-emoji> Sevimlilar — siz yoqtirgan animelarni saqlash va tez topish uchun bo‘lim.\n\n"
        f"<tg-emoji emoji-id='5436010183786513326'>❓</tg-emoji> <b>Nima qiladi?</b>\n"
        f"<tg-emoji emoji-id='5397916757333654639'>✅</tg-emoji> Sizga yoqqan animelarni saqlaydi\n"
        f"<tg-emoji emoji-id='5336993488053477866'>🚀</tg-emoji> Keyin tez ochib ko‘rish imkonini beradi\n"
        f"<tg-emoji emoji-id='5258514780469075716'>📂</tg-emoji> Barcha sevimlilar ro‘yxatini bir joyda jamlaydi\n\n"
        f"<tg-emoji emoji-id='5456429416089410910'>🛠</tg-emoji> <b>Qanday ishlaydi?</b>\n"
        f"• Anime sahifasida 🌟 Sevimlilarga qo‘shish tugmasini bosing\n"
        f"• Anime avtomatik sevimlilar ro‘yxatiga qo‘shiladi\n"
        f"• Yana bosilsa → ❌ ro‘yxatdan olib tashlanadi\n\n"
        f"<tg-emoji emoji-id='6035300138967112061'>📋</tg-emoji> <b>Sevimlilar menyusi</b>\n"
        f"Bu yerda siz saqlangan animelarni ko‘rasiz va boshqarishingiz mumkin."
    )
    await callback.message.edit_text(about_text, reply_markup=back_to_fav_keyboard(), parse_mode=ParseMode.HTML)

# --- SEVIMLILAR ICHIDAGI NAVIGATSIYA ---
@dp.callback_query(F.data == "back_to_fav")
async def back_to_fav_call(callback: types.CallbackQuery):
    user_data = await users_collection.find_one({"user_id": callback.from_user.id})
    favs = user_data.get("favorites", [])
    fav_list = "\n".join([f"{i+1}. {name}" for i, name in enumerate(favs[:10])]) if favs else "Hozircha ro'yxat bo'sh."
    
    text = (
        f"<tg-emoji emoji-id='5258259534857645678'>🌟</tg-emoji> <b>Sizning sevimli animelaringiz:</b>\n\n"
        f"{fav_list}\n\n"
        f"━━━━━━━━━━━━━━━"
    )
    await callback.message.edit_text(text, reply_markup=favorites_inline_keyboard(), parse_mode=ParseMode.HTML)

# Oxirgi qo'shilganlar
@dp.callback_query(F.data == "fav_recent")
async def fav_recent_handler(callback: types.CallbackQuery):
    text = (
        f"<tg-emoji emoji-id='5458526506886124915'>🆕</tg-emoji> <b>Yaqinda qo‘shilganlar:</b>\n"
        f"— Naruto (new)\n"
        f"— Boruto (new)"
    )
    await callback.message.edit_text(text, reply_markup=back_to_fav_keyboard(), parse_mode=ParseMode.HTML)
    
# --- TOGGLE SYSTEM (ADD/REMOVE) ---
@dp.callback_query(F.data.startswith(("add_fav_", "rem_fav_")))
async def toggle_favorite(callback: types.CallbackQuery):
    action = "add" if callback.data.startswith("add_fav_") else "remove"
    anime_id = callback.data.split("_")[-1]
    user_id = callback.from_user.id
    
    # Hozircha sinov uchun anime nomi sifatida anime_id ni olamiz
    if action == "add":
        await users_collection.update_one({"user_id": user_id}, {"$addToSet": {"favorites": anime_id}})
        await callback.answer("✅ Sevimlilarga qo‘shildi!", show_alert=False)
        await callback.message.edit_reply_markup(reply_markup=anime_item_keyboard(anime_id, is_favorite=True))
    else:
        await users_collection.update_one({"user_id": user_id}, {"$pull": {"favorites": anime_id}})
        await callback.answer("❌ Sevimlilardan olib tashlandi", show_alert=False)
        await callback.message.edit_reply_markup(reply_markup=anime_item_keyboard(anime_id, is_favorite=False))

# --- ISHGA TUSHIRISH ---
async def main():
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as e:
        logging.critical(f"Botni ishga tushirishda xato: {e}")

if __name__ == "__main__":
    asyncio.run(main())
    
