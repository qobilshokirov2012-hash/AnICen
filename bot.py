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
    profile_inline_keyboard,
    shop_inline_keyboard,
    back_to_shop_keyboard,
    main_reply_keyboard,
    favorites_inline_keyboard,
    back_to_fav_keyboard,
    anime_item_keyboard
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
            # Yangi foydalanuvchi uchun Ryo va Rank tizimi boshlang'ich qiymatlari
            await users_collection.insert_one({
                "user_id": user_id,
                "first_name": first_name,
                "ryo": 16, # Start bonusi
                "rank": "新規ユーザー (Shinki Yūza)",
                "watched_count": 0,
                "continue_count": 0,
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
@dp.message(F.text == "👤 Profil")
async def profile_handler(message: types.Message):
    user_id = message.from_user.id
    user_data = await users_collection.find_one({"user_id": user_id})
    
    if not user_data:
        await message.answer("Profil ma'lumotlari topilmadi. Iltimos, /start bosing.")
        return

    first_name = user_data.get("first_name", "Foydalanuvchi")
    username = message.from_user.username or "yo'q"
    reg_date = user_data.get("join_date").strftime("%d.%m.%Y") if user_data.get("join_date") else "Noma'lum"
    
    fav_count = len(user_data.get("favorites", []))
    watched = user_data.get("watched_count", 0)
    continuing = user_data.get("continue_count", 0)
    
    ryo = user_data.get("ryo", 16)
    rank = user_data.get("rank", "新規ユーザー (Shinki Yūza)")

    profile_text = (
        f"<b>AnICen | {first_name}</b>\n"
        f"<tg-emoji emoji-id='5332724926216428039'>👤</tg-emoji> Profil\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"<tg-emoji emoji-id='5422683699130933153'>🆔</tg-emoji> ID: <code>{user_id}</code>\n"
        f"<tg-emoji emoji-id='5879770735999717115'>👤</tg-emoji> Ism: {first_name}\n"
        f"<tg-emoji emoji-id='5879770735999717115'>🆔</tg-emoji> Username: @{username}\n"
        f"<tg-emoji emoji-id='5251537301154062376'>📅</tg-emoji> Ro‘yxatdan o‘tgan: {reg_date}\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"<tg-emoji emoji-id='5352743837502545676'>🌟</tg-emoji> Sevimlilar: {fav_count}\n"
        f"<tg-emoji emoji-id='5967411695453213733'>🎬</tg-emoji> Ko‘rilgan anime: {watched}\n"
        f"<tg-emoji emoji-id='5215677360774324968'>⏳</tg-emoji> Davom etilmoqda: {continuing}\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"<tg-emoji emoji-id='5348276504579031076'>🧠</tg-emoji> Daraja: {rank}\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"<tg-emoji emoji-id='5222126026536004111'>💴</tg-emoji> Ryo: {ryo}\n"
    )
    await message.answer(profile_text, reply_markup=profile_inline_keyboard(), parse_mode=ParseMode.HTML)

 # --- DO'KON HANDLERI (TO'G'RILANGAN) ---
@dp.callback_query(F.data == "open_shop")
async def shop_handler(callback: types.CallbackQuery):
    # Foydalanuvchi ma'lumotlarini bazadan qayta o'qiymiz
    user_data = await users_collection.find_one({"user_id": callback.from_user.id})
    
    # Agar foydalanuvchi bazada bo'lsa ryo'ni oladi, bo'lmasa 16 (yoki 0) deb belgilaydi
    ryo = user_data.get("ryo", 16) if user_data else 0
    
    text = (
        f"🛒 <b>AnICen Do‘koni</b>\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"💴 Sizning Ryo: <b>{ryo}</b>\n\n"
        f"🎌 Ranklar:\n"
        f"⚔️ Kakashi — 567 Ryo\n"
        f"🌸 Sakura — 600 Ryo\n"
        f"🗡 Sasuke — 693 Ryo\n"
        f"🍥 Naruto — 787 Ryo\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📌 Eslatma:\n"
        f"• Ranklar faqat shart bajarilgandan keyin ochiladi\n"
        f"• Xarid qilingandan so‘ng qaytarilmaydi"
    )
    await callback.message.edit_text(text, reply_markup=shop_inline_keyboard(), parse_mode=ParseMode.HTML)
    
# --- RYO HAQIDA ---
@dp.callback_query(F.data == "about_ryo")
async def about_ryo(callback: types.CallbackQuery):
    text = (
        "💴 <b>Ryo — AnICen Botning asosiy pul birligi</b>\n\n"
        "━━━━━━━━━━━━━━━\n\n"
        "🎌 <b>Ryo nima?</b>\n"
        "Ryo — anime dunyosidagi maxsus valyuta bo‘lib, bot ichidagi barcha xaridlar va darajalar uchun ishlatiladi.\n\n"
        "━━━━━━━━━━━━━━━\n\n"
        "💡 <b>Qanday ishlaydi?</b>\n"
        "• Rank sotib olish\n"
        "• Do‘kon xaridlari\n"
        "• Bonus itemlar\n\n"
        "━━━━━━━━━━━━━━━\n\n"
        "➕ <b>Ryo olish yo‘llari:</b>\n"
        "• /start → +16 Ryo\n"
        "• Anime ko‘rish → +10 Ryo\n"
        "• Do‘st taklif qilish → +26 Ryo\n"
        "• Savollarga javob → +5 Ryo\n"
        "• Kunlik topshiriqlar → bonus\n\n"
        "━━━━━━━━━━━━━━━\n\n"
        "⚠️ <b>Eslatma:</b>\n"
        "Ryo faqat bot ichida ishlatiladi va real pul emas."
    )
    await callback.message.edit_text(text, reply_markup=back_to_shop_keyboard(), parse_mode=ParseMode.HTML)

# --- DARAJA HAQIDA ---
@dp.callback_query(F.data == "about_ranks")
async def about_ranks(callback: types.CallbackQuery):
    text = (
        "🧠 <b>DARAJALAR (RANK SYSTEM)</b>\n\n"
        "🥚 <b>1. 新規ユーザー (Shinki Yūza)</b>\n"
        "🔹 Yangi foydalanuvchi\n"
        "📌 Default rank (birinchi /start)\n\n"
        "⚔️ <b>2. Kakashi</b>\n"
        "Shart:\n"
        "15 kun aktiv anime ko‘rish\n"
        "❌ 15 kundan oldin sotib bo‘lmaydi\n"
        "💴 Narx: 567 Ryo\n\n"
        "🌸 <b>3. Sakura</b>\n"
        "Shart:\n"
        "1 oy aktivlik\n"
        "📌 Har 1 anime epizod = +20 Ryo bonus\n"
        "💴 Narx: 600 Ryo\n"
        "❌ 1 oydan oldin sotib bo‘lmaydi\n\n"
        "🗡 <b>4. Sasuke</b>\n"
        "Shart:\n"
        "1.5 oy aktivlik\n"
        "📌 Har epizod = +20 Ryo\n"
        "💴 Narx: 693 Ryo\n"
        "❌ 1.5 oydan oldin sotib bo‘lmaydi\n\n"
        "🍥 <b>5. Naruto (MAX RANK)</b>\n"
        "Shart:\n"
        "2 oy aktivlik\n"
        "📌 Har epizod = +20 Ryo\n"
        "💴 Narx: 787 Ryo\n"
        "❌ 2 oydan oldin sotib bo‘lmaydi"
    )
    await callback.message.edit_text(text, reply_markup=back_to_shop_keyboard(), parse_mode=ParseMode.HTML)

# --- PROFILGA QAYTISH ---
@dp.callback_query(F.data == "back_to_profile")
async def back_to_profile(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user_data = await users_collection.find_one({"user_id": user_id})
    
    first_name = user_data.get("first_name", "Foydalanuvchi")
    username = callback.from_user.username or "yo'q"
    reg_date = user_data.get("join_date").strftime("%d.%m.%Y") if user_data.get("join_date") else "Noma'lum"
    
    fav_count = len(user_data.get("favorites", []))
    watched = user_data.get("watched_count", 0)
    continuing = user_data.get("continue_count", 0)
    ryo = user_data.get("ryo", 16)
    rank = user_data.get("rank", "新規ユーザー (Shinki Yūza)")

    profile_text = (
        f"<b>AnICen | {first_name}</b>\n"
        f"<tg-emoji emoji-id='5332724926216428039'>👤</tg-emoji> Profil\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"<tg-emoji emoji-id='5422683699130933153'>🆔</tg-emoji> ID: <code>{user_id}</code>\n"
        f"<tg-emoji emoji-id='5879770735999717115'>👤</tg-emoji> Ism: {first_name}\n"
        f"<tg-emoji emoji-id='5879770735999717115'>🆔</tg-emoji> Username: @{username}\n"
        f"<tg-emoji emoji-id='5251537301154062376'>📅</tg-emoji> Ro‘yxatdan o‘tgan: {reg_date}\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"<tg-emoji emoji-id='5352743837502545676'>🌟</tg-emoji> Sevimlilar: {fav_count}\n"
        f"<tg-emoji emoji-id='5967411695453213733'>🎬</tg-emoji> Ko‘rilgan anime: {watched}\n"
        f"<tg-emoji emoji-id='5215677360774324968'>⏳</tg-emoji> Davom etilmoqda: {continuing}\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"<tg-emoji emoji-id='5348276504579031076'>🧠</tg-emoji> Daraja: {rank}\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"<tg-emoji emoji-id='5222126026536004111'>💴</tg-emoji> Ryo: {ryo}\n"
    )
    await callback.message.edit_text(profile_text, reply_markup=profile_inline_keyboard(), parse_mode=ParseMode.HTML)

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

# --- "HAQIDA? ↓" TUGMASI ---
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
    user_id = callback.from_user.id
    user_data = await users_collection.find_one({"user_id": user_id})
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
    
