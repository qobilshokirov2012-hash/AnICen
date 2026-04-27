from aiogram import Router, F, types
from aiogram.enums import ParseMode
from motor.motor_asyncio import AsyncIOMotorClient
from os import getenv

# config.py va keyboards.py dan importlar
from config import EMOJIS
from keyboards import (
    settings_inline_keyboard,
    language_selection_keyboard,
    notifications_keyboard,
    daily_reminder_keyboard,
    anime_prefs_keyboard,
    back_to_settings_keyboard
)

router = Router()

# Ma'lumotlar bazasi ulanishi
client = AsyncIOMotorClient(getenv("MONGO_URL"))
db = client['anicen_v2']
users_collection = db['users']

# 1. SOZLAMALAR ASOSIY MENYUSI
@router.message(F.text == "⚙️ Sozlamalar")
async def settings_main_handler(message: types.Message):
    text = (
        f"<tg-emoji emoji-id='{EMOJIS['settings']}'>⚙️</tg-emoji> <b>Sozlamalar bo‘limi</b>\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"Bot interfeysini o‘zingizga moslab sozlang:\n\n"
        f"<tg-emoji emoji-id='{EMOJIS['languages']}'>🌐</tg-emoji> Tilni o‘zgartirish\n"
        f"<tg-emoji emoji-id='{EMOJIS['notify']}'>🔔</tg-emoji> Bildirishnomalar\n"
        f"<tg-emoji emoji-id='{EMOJIS['tag']}'>🏷</tg-emoji> Janr afzalliklari\n"
        f"<tg-emoji emoji-id='{EMOJIS['cup']}'>🏆</tg-emoji> Yutuqlar\n"
        f"━━━━━━━━━━━━━━━"
    )
    await message.answer(text, reply_markup=settings_inline_keyboard(), parse_mode=ParseMode.HTML)

# 2. TILNI O'ZGARTIRISH MENYUSI
@router.callback_query(F.data == "sett_lang")
async def settings_lang_menu(callback: types.CallbackQuery):
    text = (
        f"<tg-emoji emoji-id='{EMOJIS['languages']}'>🌐</tg-emoji> <b>Interfeys tilini tanlang:</b>\n\n"
        f"<tg-emoji emoji-id='{EMOJIS['uzb']}'>🇺🇿</tg-emoji> O‘zbekcha\n"
        f"<tg-emoji emoji-id='{EMOJIS['rus']}'>🇷🇺</tg-emoji> Русский\n"
        f"<tg-emoji emoji-id='{EMOJIS['eng']}'>🇬🇧</tg-emoji> English\n"
        f"<tg-emoji emoji-id='{EMOJIS['jap']}'>🇯🇵</tg-emoji> 日本語"
    )
    await callback.message.edit_text(text, reply_markup=language_selection_keyboard(), parse_mode=ParseMode.HTML)

# 3. BILDIRISHNOMALAR SOZLAMASI
@router.callback_query(F.data == "sett_notify")
async def settings_notify_handler(callback: types.CallbackQuery):
    user_data = await users_collection.find_one({"user_id": callback.from_user.id})
    is_on = user_data.get("notify", True)
    
    status_emoji = EMOJIS['correct'] if is_on else EMOJIS['off']
    status_text = "YOQILGAN" if is_on else "O‘CHIRILGAN"
    
    text = (
        f"<tg-emoji emoji-id='{EMOJIS['notify']}'>🔔</tg-emoji> <b>Bildirishnomalar boshqaruvi</b>\n\n"
        f"Hozirgi holat: <tg-emoji emoji-id='{status_emoji}'>🔘</tg-emoji> <b>{status_text}</b>\n\n"
        f"Bildirishnomalar orqali yangi animelar va muhim yangiliklardan xabardor bo‘lasiz."
    )
    await callback.message.edit_text(text, reply_markup=notifications_keyboard(), parse_mode=ParseMode.HTML)

# 4. KUNLIK ESLATMA (DAILY REMINDER)
@router.callback_query(F.data == "daily_reminder_menu")
async def daily_reminder_menu(callback: types.CallbackQuery):
    user_data = await users_collection.find_one({"user_id": callback.from_user.id})
    is_on = user_data.get("daily_reminder", True)
    
    status_emoji = EMOJIS['audio'] if is_on else EMOJIS['mute']
    
    text = (
        f"<tg-emoji emoji-id='{EMOJIS['date']}'>📅</tg-emoji> <b>Kunlik eslatmalar</b>\n\n"
        f"Holat: <tg-emoji emoji-id='{status_emoji}'>🔘</tg-emoji>\n\n"
        f"Har kuni botga kirishni unutmasligingiz uchun sizga kichik eslatma yuboramiz."
    )
    await callback.message.edit_text(text, reply_markup=daily_reminder_keyboard(), parse_mode=ParseMode.HTML)

# 5. JANR AFZALLIKLARI (PREFERENCES)
@router.callback_query(F.data == "sett_prefs")
async def settings_genres_handler(callback: types.CallbackQuery):
    text = (
        f"<tg-emoji emoji-id='{EMOJIS['tag']}'>🏷</tg-emoji> <b>Anime janrlari</b>\n\n"
        f"O‘zingizga yoqadigan janrlarni tanlang. Tizim sizga shunga qarab animelar tavsiya qiladi:"
    )
    await callback.message.edit_text(text, reply_markup=anime_prefs_keyboard(), parse_mode=ParseMode.HTML)

# 6. STATISTIKA VA YUTUQLAR (ACHIEVEMENTS)
@router.callback_query(F.data == "sett_achievements")
async def settings_stats_page(callback: types.CallbackQuery):
    user_data = await users_collection.find_one({"user_id": callback.from_user.id})
    watched = user_data.get("watched_count", 0)
    ryo = user_data.get("ryo", 0)
    
    text = (
        f"<tg-emoji emoji-id='{EMOJIS['cup']}'>🏆</tg-emoji> <b>Yutuqlaringiz</b>\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"<tg-emoji emoji-id='{EMOJIS['watched']}'>🎬</tg-emoji> Ko‘rilgan animelar: <b>{watched} ta</b>\n"
        f"<tg-emoji emoji-id='{EMOJIS['money']}'>💴</tg-emoji> Ishlab topilgan Ryo: <b>{ryo}</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"<tg-emoji emoji-id='{EMOJIS['top']}'>🔝</tg-emoji> <i>Yana 5 ta anime ko‘ring va yangi yutuqni oching!</i>"
    )
    await callback.message.edit_text(text, reply_markup=back_to_settings_keyboard(), parse_mode=ParseMode.HTML)

# 7. ORQAGA QAYTISH
@router.callback_query(F.data == "back_to_settings")
async def back_to_settings_logic(callback: types.CallbackQuery):
    await settings_main_handler(callback.message)
    await callback.message.delete()
  
