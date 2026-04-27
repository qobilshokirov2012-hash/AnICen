import asyncio
import logging
import random
from datetime import datetime, timezone
from os import getenv

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode
from motor.motor_asyncio import AsyncIOMotorClient

# Keyboards faylingizdan barcha funksiyalarni import qilamiz
from keyboards import (
    profile_inline_keyboard,
    shop_inline_keyboard,
    back_to_shop_keyboard,
    main_reply_keyboard,
    favorites_inline_keyboard,
    back_to_fav_keyboard,
    anime_item_keyboard,
    language_selection_keyboard,
    settings_inline_keyboard,
    notifications_keyboard,
    anime_prefs_keyboard,
    back_to_settings_keyboard,
    back_to_main_keyboard
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

# --- START HANDLER (TIL TANLASH BILAN) ---
@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    try:
        user_id = message.from_user.id
        user_data = await users_collection.find_one({"user_id": user_id})
        
        if not user_data:
            # Birinchi marta kirganda til tanlashni so'raymiz
            welcome_text = (
                f"<tg-emoji emoji-id='6035300138967112061'>📋</tg-emoji> <b>AnICen Botga xush kelibsiz!</b>\n\n"
                f"Boshlashdan oldin tilni tanlang <tg-emoji emoji-id='6035300138967112061'>📋</tg-emoji>\n"
                f"━━━━━━━━━━━━━━━\n\n"
                f"<tg-emoji emoji-id='5224321781321442532'>🇬🇧</tg-emoji> Please choose your language\n"
                f"<tg-emoji emoji-id='5926956071347294629'>🇯🇵</tg-emoji> 言語を選択してください\n\n"
                f"━━━━━━━━━━━━━━━\n\n"
                f"<tg-emoji emoji-id='5397782960512444700'>ℹ️</tg-emoji> Siz tanlagan til keyinchalik sozlamalarda o‘zgartirilishi mumkin"
            )
            await message.answer(welcome_text, reply_markup=language_selection_keyboard(), parse_mode=ParseMode.HTML)
        else:
            first_name = user_data.get("first_name", message.from_user.first_name)
            welcome_back = (
                f"<b>╔═══ANICEN═══╗</b>\n"
                f"<b>╚═══════════╝</b>\n\n"
                f"<tg-emoji emoji-id='{EMOJIS['welcome']}'>👋</tg-emoji> Salom, <b>{first_name}</b>!\n\n"
                f"Qaytganingizdan xursandmiz. Trend animelar sizni kutmoqda!\n\n"
                f"<tg-emoji emoji-id='{EMOJIS['start']}'>⚡</tg-emoji> Boshlash uchun menyudan foydalaning:"
            )
            await message.answer(welcome_back, reply_markup=main_reply_keyboard(), parse_mode=ParseMode.HTML)
    except Exception as e:
        logging.error(f"Start xatosi: {e}")

# --- TILNI TANLASH CALLBACK ---
@dp.callback_query(F.data.startswith("set_lang_"))
async def set_language_handler(callback: types.CallbackQuery):
    lang_code = callback.data.split("_")[-1]
    user_id = callback.from_user.id
    
    await users_collection.update_one(
        {"user_id": user_id},
        {"$set": {
            "lang": lang_code,
            "first_name": callback.from_user.first_name,
            "ryo": 16,
            "rank": "新規ユーザー (Shinki Yūza)",
            "watched_count": 0,
            "continue_count": 0,
            "favorites": [],
            "notify": True,
            "join_date": datetime.now(timezone.utc)
        }},
        upsert=True
    )
    
    await callback.message.delete()
    await callback.message.answer(f"✅ Til o'rnatildi! Botdan foydalanishingiz mumkin.", reply_markup=main_reply_keyboard())

# --- PROFIL HANDLERI ---
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
    # --- DO'KON HANDLERI ---
@dp.callback_query(F.data == "open_shop")
async def shop_handler(callback: types.CallbackQuery):
    user_data = await users_collection.find_one({"user_id": callback.from_user.id})
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

# --- RYO VA DARAJA HAQIDA MA'LUMOT ---
@dp.callback_query(F.data == "about_ryo")
async def about_ryo_handler(callback: types.CallbackQuery):
    text = (
        "💴 <b>Ryo — AnICen Botning asosiy pul birligi</b>\n\n"
        "━━━━━━━━━━━━━━━\n\n"
        "🎌 <b>Ryo nima?</b>\n"
        "Ryo — anime dunyosidagi maxsus valyuta bo‘lib, bot ichidagi barcha xaridlar va darajalar uchun ishlatiladi.\n\n"
        "💡 <b>Qanday ishlaydi?</b>\n"
        "• Rank sotib olish\n"
        "• Do‘kon xaridlari\n"
        "• Bonus itemlar\n\n"
        "➕ <b>Ryo olish yo‘llari:</b>\n"
        "• /start → +16 Ryo\n"
        "• Anime ko‘rish → +10 Ryo\n"
        "• Do‘st taklif qilish → +26 Ryo\n"
        "• Kunlik topshiriqlar → bonus"
    )
    await callback.message.edit_text(text, reply_markup=back_to_shop_keyboard(), parse_mode=ParseMode.HTML)

@dp.callback_query(F.data == "about_ranks")
async def about_ranks_handler(callback: types.CallbackQuery):
    text = (
        "🧠 <b>DARAJALAR (RANK SYSTEM)</b>\n\n"
        "⚔️ <b>2. Kakashi</b>\n"
        "Shart: 15 kun aktivlik\n"
        "💴 Narx: 567 Ryo\n\n"
        "🌸 <b>3. Sakura</b>\n"
        "Shart: 1 oy aktivlik\n"
        "💴 Narx: 600 Ryo\n\n"
        "🗡 <b>4. Sasuke</b>\n"
        "Shart: 1.5 oy aktivlik\n"
        "💴 Narx: 693 Ryo\n\n"
        "🍥 <b>5. Naruto (MAX)</b>\n"
        "Shart: 2 oy aktivlik\n"
        "💴 Narx: 787 Ryo"
    )
    await callback.message.edit_text(text, reply_markup=back_to_shop_keyboard(), parse_mode=ParseMode.HTML)

# --- SOZLAMALAR ASOSIY HANDLERI ---
@dp.message(F.text == "⚙️ Sozlamalar")
async def settings_main_handler(message: types.Message):
    text = (
        f"<tg-emoji emoji-id='5341715473882955310'>⚙️</tg-emoji> <b>Sozlamalar</b>\n\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"<tg-emoji emoji-id='5332724926216428039'>👤</tg-emoji> <b>Foydalanuvchi sozlamalari:</b>\n"
        f"• Til\n"
        f"• Bildirishnomalar\n"
        f"• Maxfiylik\n"
        f"• UI uslubi\n\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"<tg-emoji emoji-id='5341715473882955310'>⚙️</tg-emoji> <b>Anime bot sozlamalari:</b>\n"
        f"• Auto recommend anime\n"
        f"• Daily reminder\n"
        f"• XP display\n\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"<tg-emoji emoji-id='5260752634523969530'>🛠</tg-emoji> Kerakli bo‘limni tanlang:"
    )
    await message.answer(text, reply_markup=settings_inline_keyboard(), parse_mode=ParseMode.HTML)

# --- BILDIRISHNOMALAR VA UI ---
@dp.callback_query(F.data == "sett_notify")
async def settings_notify_handler(callback: types.CallbackQuery):
    user_data = await users_collection.find_one({"user_id": callback.from_user.id})
    status = user_data.get("notify", True)
    text = (
        f"<tg-emoji emoji-id='5458603043203327669'>🔔</tg-emoji> <b>Bildirishnomalar</b>\n\n"
        f"Holat: <b>{'YOQILGAN' if status else 'OʻCHIRILGAN'}</b>"
    )
    await callback.message.edit_text(text, reply_markup=notifications_keyboard(status), parse_mode=ParseMode.HTML)

@dp.callback_query(F.data == "sett_ui")
async def settings_ui_handler(callback: types.CallbackQuery):
    text = (
        f"<tg-emoji emoji-id='5238221051405549815'>🎨</tg-emoji> <b>UI uslubi</b>\n\n"
        f"Joriy: <b>Anime Dark Mode</b>"
    )
    await callback.message.edit_text(text, reply_markup=back_to_settings_keyboard(), parse_mode=ParseMode.HTML)

# --- ANIME PREFERENCES ---
@dp.callback_query(F.data == "sett_prefs")
async def settings_prefs_handler(callback: types.CallbackQuery):
    text = (
        f"🎌 <b>Anime sozlamalari</b>\n\n"
        f"Sevimli janrlar:\n"
        f"• Action\n"
        f"• Romance\n"
        f"• Adventure\n"
        f"• Fantasy"
    )
    await callback.message.edit_text(text, reply_markup=anime_prefs_keyboard(), parse_mode=ParseMode.HTML)

# --- ACHIEVEMENT SYSTEM ---
@dp.callback_query(F.data == "sett_achievements")
async def settings_achievements_handler(callback: types.CallbackQuery):
    user_data = await users_collection.find_one({"user_id": callback.from_user.id})
    watched = user_data.get("watched_count", 0)
    # Bu yerda mantiqiy hisob-kitoblar (namuna sifatida)
    active_days = 1 
    invites = 0
    
    text = (
        f"🎖 <b>Yutuqlar:</b>\n\n"
        f"• 🎬 <b>{watched}</b> anime ko‘rdi → <b>+{watched * 10}</b> Ryo\n"
        f"• 🔥 <b>{active_days}</b> kun aktiv → <b>+{active_days * 13}</b> Ryo\n"
        f"• 👥 <b>{invites}</b> do‘st taklif → <b>+{invites * 26}</b> Ryo"
    )
    await callback.message.edit_text(text, reply_markup=back_to_settings_keyboard(), parse_mode=ParseMode.HTML)

# --- PROFILGA QAYTISH (CALLBACK) ---
@dp.callback_query(F.data == "back_to_profile")
async def back_to_profile_callback(callback: types.CallbackQuery):
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
        f"💴 Ryo: {ryo}\n"
        f"🧠 Daraja: {rank}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🌟 Sevimlilar: {fav_count}\n"
        f"🎬 Ko‘rilgan: {watched}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🆔 ID: <code>{user_id}</code>"
    )
    await callback.message.edit_text(profile_text, reply_markup=profile_inline_keyboard(), parse_mode=ParseMode.HTML)

# --- BOSHQARUV TUGMALARI ---
@dp.callback_query(F.data == "back_to_settings")
async def back_to_settings_handler(callback: types.CallbackQuery):
    await callback.message.edit_text("Kerakli bo‘limni tanlang:", reply_markup=settings_inline_keyboard())

@dp.callback_query(F.data == "close_settings")
async def close_settings_handler(callback: types.CallbackQuery):
    await callback.message.delete()

# --- ISHGA TUSHIRISH ---
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
