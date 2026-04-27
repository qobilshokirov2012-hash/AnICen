import asyncio
import logging
from datetime import datetime, timezone
from os import getenv

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode
from motor.motor_asyncio import AsyncIOMotorClient

# main_reply_keyboard'ni ham import qilamiz
from keyboards import main_menu_keyboard, main_reply_keyboard, back_to_main_keyboard
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

        # Bu yerda reply_markup o'zgardi: Endi pastdagi doimiy menyu chiqadi
        await message.answer(welcome_text, reply_markup=main_reply_keyboard(), parse_mode=ParseMode.HTML)

    except Exception as e:
        logging.error(f"Xatolik: {e}")

# --- REPLY MENYU TUGMALARI UCHUN HANDLERLAR ---
# Bu qismlar tugmalar bosilganda javob berishi uchun kerak

@dp.message(F.text == "🔍 Qidirish")
async def search_handler(message: types.Message):
    await message.answer("🔍 Anime nomini kiriting:", reply_markup=back_to_main_keyboard())

@dp.message(F.text == "👤 Profil")
async def profile_handler(message: types.Message):
    # Siz aytgan /ADK buyrug'ini shu yerda chaqiramiz
    user_data = await users_collection.find_one({"user_id": message.from_user.id})
    points = user_data.get("points", 0) if user_data else 0
    await message.answer(f"👤 <b>Profilingiz</b>\n\n💰 Ballaringiz: {points} ball\nBuyruq: /ADK", parse_mode=ParseMode.HTML)

@dp.message(Command("ADK"))
async def adk_handler(message: types.Message):
    # /ADK buyrug'i uchun alohida handler
    await profile_handler(message)

@dp.message(F.text == "🎲 Tasodifiy Anime")
async def random_handler(message: types.Message):
    await message.answer("🎲 Tasodifiy anime qidirilmoqda...")

# Profil callback uchun (Inline tugma bosilsa)
@dp.callback_query(F.data == "cmd_adk")
async def profile_via_adk(callback: types.CallbackQuery):
    await callback.answer("Profilingizni ko'rish uchun /ADK buyrug'ini yuboring!", show_alert=True)

# --- ISHGA TUSHIRISH ---
async def main():
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as e:
        logging.critical(f"Botni ishga tushirishda xato: {e}")

if __name__ == "__main__":
    asyncio.run(main())
        
# --- SEVIMLILAR BO'LIMI (REPLY TUGMA) ---
@dp.message(F.text == "🌟 Sevimlilar")
async def favorites_handler(message: types.Message):
    user_id = message.from_user.id
    user_data = await users_collection.find_one({"user_id": user_id})
    favs = user_data.get("favorites", [])
    
    # Ro'yxatni shakllantirish
    if not favs:
        fav_list = "Hozircha sevimlilar ro'yxatingiz bo'sh."
    else:
        fav_list = "\n".join([f"{i+1}. {name}" for i, name in enumerate(favs[:5])]) # Dastlabki 5tasi

    text = (
        f"<tg-emoji emoji-id='5258259534857645678'>🌟</tg-emoji> Sizning sevimli animelaringiz:\n\n"
        f"{fav_list}\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"<tg-emoji emoji-id='5352743837502545676'>🌟</tg-emoji> <b>Sevimlilar (Favorites)</b>\n"
        f"<tg-emoji emoji-id='5442875573045045415'>📄</tg-emoji> Sevimlilar — siz yoqtirgan animelarni saqlash va tez topish uchun bo‘lim.\n\n"
        f"<tg-emoji emoji-id='5436010183786513326'>❓</tg-emoji> <b>Nima qiladi?</b>\n"
        f"<tg-emoji emoji-id='5397916757333654639'>✅</tg-emoji> Sizga yoqqan animelarni saqlaydi\n"
        f"<tg-emoji emoji-id='5336993488053477866'>🚀</tg-emoji> Keyin tez ochib ko‘rish imkonini beradi\n"
        f"<tg-emoji emoji-id='5258514780469075716'>📂</tg-emoji> Barcha sevimlilar ro‘yxatini bir joyda jamlaydi\n\n"
        f"<tg-emoji emoji-id='5456429416089410910'>🛠</tg-emoji> <b>Qanday ishlaydi?</b>\n"
        f"• Anime sahifasida <tg-emoji emoji-id='5352743837502545676'>🌟</tg-emoji> Sevimlilarga qo‘shish tugmasini bosing\n"
        f"• Anime avtomatik sevimlilar ro‘yxatiga qo‘shiladi\n"
        f"• Yana bosilsa → <tg-emoji emoji-id='5949785428843302949'>❌</tg-emoji> ro‘yxatdan olib tashlanadi\n\n"
        f"<tg-emoji emoji-id='6035300138967112061'>📋</tg-emoji> <b>Sevimlilar menyusi</b>\n"
        f"Bu yerda siz:\n"
        f"<tg-emoji emoji-id='5258514780469075716'>📂</tg-emoji> Saqlangan animelarni ko‘rasiz\n"
        f"<tg-emoji emoji-id='5336993488053477866'>🔍</tg-emoji> Har bir anime sahifasini ochasiz\n"
        f"<tg-emoji emoji-id='5949785428843302949'>🗑</tg-emoji> Keraksizlarini olib tashlaysiz"
    )

    await message.answer(text, reply_markup=favorites_inline_keyboard(), parse_mode=ParseMode.HTML)

# --- OXIRGI QO'SHILGANLAR (1 KUNLIK NEW BELGISI BILAN) ---
@dp.callback_query(F.data == "fav_recent")
async def fav_recent_handler(callback: types.CallbackQuery):
    # Bu yerda mantiqan oxirgi 24 soatda qo'shilganlar filtrlanadi
    text = (
        f"<tg-emoji emoji-id='5458526506886124915'>🆕</tg-emoji> <b>Yaqinda qo‘shilganlar:</b>\n"
        f"— Naruto (new)\n"
        f"— Boruto (new)"
    )
    await callback.message.edit_text(text, reply_markup=back_to_main_keyboard(), parse_mode=ParseMode.HTML)

# --- TOGGLE SYSTEM (QO'SHISH VA OLIB TASHLASH) ---
@dp.callback_query(F.data.startswith("add_fav_"))
async def add_to_favorites(callback: types.CallbackQuery):
    anime_id = callback.data.split("_")[-1]
    user_id = callback.from_user.id
    
    # Bazaga qo'shish (Misol: "Naruto")
    await users_collection.update_one(
        {"user_id": user_id},
        {"$addToSet": {"favorites": "Naruto"}} # Bu yerda anime_id bo'yicha nom olinadi
    )
    
    await callback.answer("✅ Sevimlilarga qo‘shildi!", show_alert=False)
    # Tugmani o'zgartiramiz
    await callback.message.edit_reply_markup(reply_markup=anime_item_keyboard(anime_id, is_favorite=True))

@dp.callback_query(F.data.startswith("rem_fav_"))
async def remove_from_favorites(callback: types.CallbackQuery):
    anime_id = callback.data.split("_")[-1]
    user_id = callback.from_user.id
    
    # Bazadan olib tashlash
    await users_collection.update_one(
        {"user_id": user_id},
        {"$pull": {"favorites": "Naruto"}}
    )
    
    await callback.answer("❌ Sevimlilardan olib tashlandi", show_alert=False)
    # Tugmani qaytaramiz
    await callback.message.edit_reply_markup(reply_markup=anime_item_keyboard(anime_id, is_favorite=False))
