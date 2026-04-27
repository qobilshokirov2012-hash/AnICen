import asyncio
import logging
import random
from datetime import datetime, timezone
from os import getenv

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode
from motor.motor_asyncio import AsyncIOMotorClient

# keyboard.py faylingizdan importlar
from keyboards import (
    main_reply_keyboard,
    language_selection_keyboard,
    profile_inline_keyboard,
    shop_inline_keyboard,
    back_to_shop_keyboard,
    settings_inline_keyboard,
    notifications_keyboard,
    daily_reminder_keyboard,
    favorites_inline_keyboard,
    anime_prefs_keyboard,
    back_to_settings_keyboard
)

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
            welcome_text = (
                f"📋 <b>AnICen Botga xush kelibsiz!</b>\n\n"
                f"Boshlashdan oldin tilni tanlang 📋\n"
                f"━━━━━━━━━━━━━━━\n\n"
                f"🇬🇧 Please choose your language\n"
                f"🇯🇵 言語を選択してください\n\n"
                f"━━━━━━━━━━━━━━━\n\n"
                f"ℹ️ Siz tanlagan til keyinchalik sozlamalarda o‘zgartirilishi mumkin"
            )
            await message.answer(welcome_text, reply_markup=language_selection_keyboard(), parse_mode=ParseMode.HTML)
        else:
            first_name = user_data.get("first_name", message.from_user.first_name)
            welcome_back = (
                f"<b>╔═══ANICEN═══╗</b>\n"
                f"<b>╚═══════════╝</b>\n\n"
                f"👋 Salom, <b>{first_name}</b>!\n\n"
                f"Qaytganingizdan xursandmiz. Trend animelar sizni kutmoqda!\n\n"
                f"⚡ Boshlash uchun menyudan foydalaning:"
            )
            await message.answer(welcome_back, reply_markup=main_reply_keyboard(), parse_mode=ParseMode.HTML)
    except Exception as e:
        logging.error(f"Start xatosi: {e}")

# --- TILNI TANLASH CALLBACK ---
@dp.callback_query(F.data.startswith("set_lang_"))
async def set_language_handler(callback: types.CallbackQuery):
    lang_code = callback.data.split("_")[-1]
    user_id = callback.from_user.id
    
    await callback.answer("Til o'rnatilmoqda...", show_alert=False)
    
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
            "daily_reminder": True,
            "join_date": datetime.now(timezone.utc)
        }},
        upsert=True
    )
    
    await callback.message.delete()
    await callback.message.answer(
        f"✅ Til muvaffaqiyatli o'rnatildi! Botdan to'liq foydalanishingiz mumkin.", 
        reply_markup=main_reply_keyboard()
    )

# --- PROFIL HANDLERI (/ADK VA TUGMA) ---
@dp.message(Command("ADK"))
@dp.message(F.text == "👤 Profil")
async def profile_handler(message: types.Message):
    user_id = message.from_user.id
    user_data = await users_collection.find_one({"user_id": user_id})
    
    if not user_data:
        await message.answer("Profil ma'lumotlari topilmadi. Iltimos, /start bosing.")
        return

    first_name = user_data.get("first_name", message.from_user.first_name)
    username = message.from_user.username or "yo'q"
    reg_date = user_data.get("join_date").strftime("%d.%m.%Y") if user_data.get("join_date") else "Noma'lum"
    
    fav_count = len(user_data.get("favorites", []))
    watched = user_data.get("watched_count", 0)
    ryo = user_data.get("ryo", 16)
    rank = user_data.get("rank", "新規ユーザー (Shinki Yūza)")

    profile_text = (
        f"<b>AnICen | {first_name}</b>\n"
        f"👤 <b>Profil</b>\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🆔 ID: <code>{user_id}</code>\n"
        f"👤 Ism: {first_name}\n"
        f"📅 Qo'shilgan: {reg_date}\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🌟 Sevimlilar: {fav_count}\n"
        f"🎬 Ko‘rilgan: {watched}\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🧠 Daraja: {rank}\n"
        f"💴 Ryo: {ryo}\n"
    )
    await message.answer(profile_text, reply_markup=profile_inline_keyboard(), parse_mode=ParseMode.HTML)

# --- DO'KON HANDLERI (REPLY TUGMA ORQALI) ---
@dp.message(F.text == "🛒 Do‘kon")
async def shop_reply_handler(message: types.Message):
    user_data = await users_collection.find_one({"user_id": message.from_user.id})
    ryo = user_data.get("ryo", 0) if user_data else 0
    
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
    await message.answer(text, reply_markup=shop_inline_keyboard(), parse_mode=ParseMode.HTML)

# --- DO'KON (INLINE CALLBACK ORQALI - PROFILDAN KIRGANDA) ---
@dp.callback_query(F.data == "open_shop")
async def shop_callback_handler(callback: types.CallbackQuery):
    user_data = await users_collection.find_one({"user_id": callback.from_user.id})
    ryo = user_data.get("ryo", 0) if user_data else 0
    
    text = (
        f"🛒 <b>AnICen Do‘koni</b>\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"💴 Sizning Ryo: <b>{ryo}</b>\n\n"
        f"🎌 Ranklar:\n"
        f"⚔️ Kakashi — 567 Ryo\n"
        f"🌸 Sakura — 600 Ryo\n"
        f"🗡 Sasuke — 693 Ryo\n"
        f"🍥 Naruto — 787 Ryo\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"Sotib olish uchun darajani tanlang:"
    )
    await callback.message.edit_text(text, reply_markup=shop_inline_keyboard(), parse_mode=ParseMode.HTML)

# --- RANK SOTIB OLISH VA RYO TEKSHIRISH ---
@dp.callback_query(F.data.startswith("buy_rank_"))
async def buy_rank_handler(callback: types.CallbackQuery):
    rank_key = callback.data.split("_")[-1]
    prices = {
        "kakashi": 567,
        "sakura": 600,
        "sasuke": 693,
        "naruto": 787
    }
    price = prices.get(rank_key)
    
    user_data = await users_collection.find_one({"user_id": callback.from_user.id})
    current_ryo = user_data.get("ryo", 0)
    
    if current_ryo < price:
        # RYO YETMASA EKRANDA ALERT CHIQARISH
        await callback.answer("❌ Sizning Ryoyingiz yetarli emas!", show_alert=True)
    else:
        # Sotib olish logikasi
        new_ryo = current_ryo - price
        rank_names = {
            "kakashi": "はたけカカシ (Hatake Kakashi)",
            "sakura": "春野サクラ (Haruno Sakura)",
            "sasuke": "うちはサスケ (Uchiha Sasuke)",
            "naruto": "うずまきナルト (Uzumaki Naruto)"
        }
        new_rank = rank_names.get(rank_key)
        
        await users_collection.update_one(
            {"user_id": callback.from_user.id},
            {"$set": {"ryo": new_ryo, "rank": new_rank}}
        )
        await callback.answer(f"✅ Tabriklaymiz! Siz {rank_key.capitalize()} darajasini sotib oldingiz!", show_alert=True)
        # Ekranni yangilash
        await shop_callback_handler(callback)

# --- RYO VA DARAJA HAQIDA MA'LUMOT ---
@dp.callback_query(F.data == "about_ryo")
async def about_ryo_handler(callback: types.CallbackQuery):
    text = (
        "💴 <b>Ryo — AnICen Botning asosiy pul birligi</b>\n\n"
        "🎌 <b>Ryo nima?</b>\n"
        "Ryo — anime dunyosidagi maxsus valyuta bo‘lib, bot ichidagi barcha xaridlar va darajalar uchun ishlatiladi.\n\n"
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
        "⚔️ <b>2. Kakashi</b> — 567 Ryo\n"
        "🌸 <b>3. Sakura</b> — 600 Ryo\n"
        "🗡 <b>4. Sasuke</b> — 693 Ryo\n"
        "🍥 <b>5. Naruto (MAX)</b> — 787 Ryo\n\n"
        "<i>Eslatma: Darajalar sizning botdagi nufuzingizni belgilaydi.</i>"
    )
    await callback.message.edit_text(text, reply_markup=back_to_shop_keyboard(), parse_mode=ParseMode.HTML)
# --- SOZLAMALAR ASOSIY HANDLERI ---
@dp.message(F.text == "⚙️ Sozlamalar")
async def settings_main_handler(message: types.Message):
    text = (
        f"⚙️ <b>Sozlamalar</b>\n\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"👤 <b>Foydalanuvchi sozlamalari:</b>\n"
        f"• Tilni almashtirish\n"
        f"• Bildirishnomalar boshqaruvi\n"
        f"• UI uslubi va ko'rinish\n\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"🛠 <b>Bot funksiyalari:</b>\n"
        f"• Avtomatik anime tavsiyalari\n"
        f"• Kunlik topshiriq eslatmalari\n\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"Kerakli bo‘limni tanlang:"
    )
    await message.answer(text, reply_markup=settings_inline_keyboard(), parse_mode=ParseMode.HTML)

# --- BILDIRISHNOMALAR (REPLY TUGMA ORQALI) ---
@dp.message(F.text == "🔔 Bildirishnomalar")
async def notifications_reply_handler(message: types.Message):
    # Bu handler foydalanuvchi reply menyudagi tugmani bosganda ishlaydi
    await settings_notify_handler(message)

# --- BILDIRISHNOMALAR MENYUSI (PREMIUM FORMAT) ---
@dp.callback_query(F.data == "sett_notify")
@dp.message(F.text == "🔔 Bildirishnomalar") # Ikkala holatda ham ishlashi uchun
async def settings_notify_handler(event: types.Message | types.CallbackQuery):
    user_id = event.from_user.id
    user_data = await users_collection.find_one({"user_id": user_id})
    
    is_on = user_data.get("notify", True)
    status_text = "🟢 ON" if is_on else "🔴 OFF"
    
    text = (
        f"🔔 <b>Bildirishnomalar</b>\n\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"Holat: <b>{status_text}</b>\n\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"Quyidagilar haqida xabar olasiz:\n"
        f"• Kunlik topshiriqlar\n"
        f"• Yangi anime tavsiyalari\n"
        f"• Mukofot va bonuslar\n"
        f"• Yangilanishlar\n\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"Kerakli sozlamani tanlang:"
    )
    
    if isinstance(event, types.Message):
        await event.answer(text, reply_markup=notifications_keyboard(), parse_mode=ParseMode.HTML)
    else:
        await event.message.edit_text(text, reply_markup=notifications_keyboard(), parse_mode=ParseMode.HTML)

# --- BILDIRISHNOMA ON/OFF TOGGLE ---
@dp.callback_query(F.data.in_({"notify_on", "notify_off"}))
async def toggle_notify_handler(callback: types.CallbackQuery):
    is_on = callback.data == "notify_on"
    await users_collection.update_one(
        {"user_id": callback.from_user.id}, 
        {"$set": {"notify": is_on}}
    )
    
    if is_on:
        alert_msg = "✅ Bildirishnomalar yoqildi\n\nEndi siz muhim yangiliklar va topshiriqlar haqida xabar olasiz"
    else:
        alert_msg = "❌ Bildirishnomalar o‘chirildi\n\nEndi sizga xabar yuborilmaydi"
        
    await callback.answer(alert_msg, show_alert=True)
    # Menyuni yangilash
    await settings_notify_handler(callback)

# --- DAILY REMINDER MENYUSI ---
@dp.callback_query(F.data == "daily_reminder_menu")
async def daily_reminder_handler(callback: types.CallbackQuery):
    user_data = await users_collection.find_one({"user_id": callback.from_user.id})
    is_on = user_data.get("daily_reminder", True)
    status_text = "🟢 ON" if is_on else "🔴 OFF"
    
    text = (
        f"📅 <b>Daily reminder</b>\n\n"
        f"Holat: <b>{status_text}</b>\n\n"
        f"Har kuni sizga kunlik topshiriqlar haqida eslatma yuboriladi\n\n"
        f"⏰ <b>QACHON YUBORILADI?</b>\n"
        f"👉 Tavsiya: Har kuni 18:00 yoki 20:00\n"
        f"<i>(User local time bo‘yicha)</i>\n\n"
        f"🎯 <b>Soft push xabari:</b>\n"
        f"<i>Bugun hali aktiv emassiz 👀\n"
        f"Bir nechta topshiriq bajarib, Ryo ishlab oling!</i>"
    )
    await callback.message.edit_text(text, reply_markup=daily_reminder_keyboard(), parse_mode=ParseMode.HTML)

# --- DAILY REMINDER TOGGLE ---
@dp.callback_query(F.data.in_({"remind_on", "remind_off"}))
async def toggle_reminder_handler(callback: types.CallbackQuery):
    is_on = callback.data == "remind_on"
    await users_collection.update_one(
        {"user_id": callback.from_user.id}, 
        {"$set": {"daily_reminder": is_on}}
    )
    
    # Kichik xabar
    status = "yoqildi" if is_on else "o'chirildi"
    await callback.answer(f"Eslatma {status}")
    await daily_reminder_handler(callback)

# --- ANIME PREFERENCES ---
@dp.callback_query(F.data == "sett_prefs")
async def settings_prefs_handler(callback: types.CallbackQuery):
    text = (
        f"🎌 <b>Anime sozlamalari</b>\n\n"
        f"Qaysi janrdagi animelarni afzal ko'rasiz?\n"
        f"Tizim shunga qarab sizga tavsiyalar beradi."
    )
    await callback.message.edit_text(text, reply_markup=anime_prefs_keyboard(), parse_mode=ParseMode.HTML)

# --- ORQAGA QAYTISH VA YOPISH ---
@dp.callback_query(F.data == "back_to_settings")
async def back_to_settings_callback(callback: types.CallbackQuery):
    await callback.message.edit_text("Kerakli bo‘limni tanlang:", reply_markup=settings_inline_keyboard())

@dp.callback_query(F.data == "close_settings")
async def close_settings_callback(callback: types.CallbackQuery):
    await callback.message.delete()

# --- SEVIMLILAR BO'LIMI (REPLY TUGMA) ---
@dp.message(F.text == "🌟 Sevimlilar")
async def favorites_handler(message: types.Message):
    user_id = message.from_user.id
    user_data = await users_collection.find_one({"user_id": user_id})
    
    if not user_data:
        await message.answer("Profil topilmadi. /start bosing.")
        return
        
    favs = user_data.get("favorites", [])
    
    if not favs:
        fav_list = "Hozircha ro'yxatingiz bo'sh. \nAnimelarga kirib 🌟 tugmasini bosing!"
    else:
        # Ro'yxatni chiroyli formatda chiqarish
        fav_list = "Siz yoqtirgan animelar:\n\n"
        for i, name in enumerate(favs[:10], 1): # Dastlabki 10 tasini ko'rsatish
            fav_list += f"{i}. <b>{name}</b>\n"
            
    text = (
        f"🌟 <b>Sevimlilaringiz</b>\n\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"{fav_list}\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"Barcha sevimlilarni boshqarish uchun pastdagi tugmalardan foydalaning:"
    )
    await message.answer(text, reply_markup=favorites_inline_keyboard(), parse_mode=ParseMode.HTML)

# --- ACHIEVEMENT SYSTEM (YUTUQLAR) ---
@dp.callback_query(F.data == "sett_achievements")
async def settings_achievements_handler(callback: types.CallbackQuery):
    user_data = await users_collection.find_one({"user_id": callback.from_user.id})
    
    if not user_data:
        await callback.answer("Ma'lumot topilmadi")
        return
        
    watched = user_data.get("watched_count", 0)
    # Namuna uchun hisob-kitoblar (Buni o'zingizning mantiqingizga moslab o'zgartirishingiz mumkin)
    active_days = 1 
    invites = 0
    
    # Har bir ko'rilgan anime uchun 10 ryo, har bir kun uchun 13 ryo bonus sifatida ko'rsatiladi
    text = (
        f"🎖 <b>Yutuqlar va Statistika:</b>\n\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"🎬 <b>Ko'rilgan:</b> {watched} anime\n"
        f"💰 Ishlangan: <b>+{watched * 10}</b> Ryo\n\n"
        f"🔥 <b>Aktivlik:</b> {active_days} kun\n"
        f"💰 Ishlangan: <b>+{active_days * 13}</b> Ryo\n\n"
        f"👥 <b>Takliflar:</b> {invites} do'st\n"
        f"💰 Ishlangan: <b>+{invites * 26}</b> Ryo\n\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"<i>Ko'proq anime ko'ring va darajangizni oshiring!</i>"
    )
    await callback.message.edit_text(text, reply_markup=back_to_settings_keyboard(), parse_mode=ParseMode.HTML)

# --- UI USLUBU ---
@dp.callback_query(F.data == "sett_ui")
async def settings_ui_handler(callback: types.CallbackQuery):
    text = (
        f"🎨 <b>UI uslubi va ko'rinish</b>\n\n"
        f"Hozirgi uslub: <b>Anime Dark Mode (Default)</b>\n\n"
        f"Bu bo'limda botning xabarlar ko'rinishini o'zgartirishingiz mumkin bo'ladi.\n"
        f"<i>(Tez kunda yangi mavzular qo'shiladi!)</i>"
    )
    await callback.message.edit_text(text, reply_markup=back_to_settings_keyboard(), parse_mode=ParseMode.HTML)

# --- BOTNI ISHGA TUSHIRISH (MAIN) ---
async def main():
    # Eski xabarlarni (webhook) tozalash
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Botni polling rejimida ishga tushirish
    print("Bot muvaffaqiyatli ishga tushdi! ✅")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot to'xtatildi! 🛑")
        
