from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from config import EMOJIS

# --- 1. ASOSIY REPLY MENYU ---
def main_reply_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="🌟 Sevimlilar"), KeyboardButton(text="👤 Profil"))
    builder.row(KeyboardButton(text="🛒 Do‘kon"), KeyboardButton(text="⚙️ Sozlamalar"))
    builder.row(KeyboardButton(text="🔔 Bildirishnomalar"))
    return builder.as_markup(resize_keyboard=True)

# --- 2. TILNI TANLASH (INLINE) ---
def language_selection_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="set_lang_uz"))
    builder.add(InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_lang_ru"))
    builder.add(InlineKeyboardButton(text="🇬🇧 English", callback_data="set_lang_en"))
    builder.add(InlineKeyboardButton(text="🇯🇵 日本語", callback_data="set_lang_jp"))
    builder.adjust(2)
    return builder.as_markup()

# --- 3. PROFIL VA DO'KON TUGMALARI ---
def profile_inline_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🛒 Do'konga kirish", callback_data="open_shop"))
    builder.row(InlineKeyboardButton(text="🏆 Yutuqlar", callback_data="sett_achievements"))
    return builder.as_markup()

def shop_inline_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🥷 Kakashi (567 Ryo)", callback_data="buy_rank_kakashi"))
    builder.add(InlineKeyboardButton(text="👓 Gojo (600 Ryo)", callback_data="buy_rank_gojo"))
    builder.add(InlineKeyboardButton(text="🍥 Naruto (787 Ryo)", callback_data="buy_rank_naruto"))
    builder.row(InlineKeyboardButton(text="❓ Ryo haqida", callback_data="about_ryo"))
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_settings"))
    builder.adjust(1)
    return builder.as_markup()

def back_to_shop_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="⬅️ Do'konga qaytish", callback_data="open_shop"))
    return builder.as_markup()

# --- 4. SOZLAMALAR BO'LIMI ---
def settings_inline_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🌐 Tilni o'zgartirish", callback_data="sett_lang"))
    builder.add(InlineKeyboardButton(text="🔔 Bildirishnomalar", callback_data="sett_notify"))
    builder.add(InlineKeyboardButton(text="🏷 Janrlar", callback_data="sett_prefs"))
    builder.add(InlineKeyboardButton(text="📊 Statistika", callback_data="sett_achievements"))
    builder.adjust(2)
    return builder.as_markup()

def notifications_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🔔 Yoqish", callback_data="notify_on"))
    builder.add(InlineKeyboardButton(text="🔕 O'chirish", callback_data="notify_off"))
    builder.row(InlineKeyboardButton(text="📅 Kunlik eslatma", callback_data="daily_reminder_menu"))
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_settings"))
    builder.adjust(2, 1, 1)
    return builder.as_markup()

def daily_reminder_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="✅ Yoqish", callback_data="remind_on"))
    builder.add(InlineKeyboardButton(text="❌ O'chirish", callback_data="remind_off"))
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="sett_notify"))
    builder.adjust(2, 1)
    return builder.as_markup()

def anime_prefs_keyboard():
    builder = InlineKeyboardBuilder()
    janrlar = ["Shonen", "Seinen", "Romantika", "Action", "Drama", "🎲 Random"]
    for j in janrlar:
        builder.add(InlineKeyboardButton(text=j, callback_data=f"pref_{j.lower()}"))
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_settings"))
    builder.adjust(2)
    return builder.as_markup()

def back_to_settings_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_settings"))
    return builder.as_markup()

# --- 5. SEVIMLILAR BO'LIMI ---
def favorites_inline_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="ℹ️ Haqida", callback_data="fav_about"))
    builder.add(InlineKeyboardButton(text="🕒 Oxirgi qo'shilganlar", callback_data="fav_recent"))
    builder.row(InlineKeyboardButton(text="🗑 Hammasini o'chirish", callback_data="clear_favorites"))
    builder.adjust(2, 1)
    return builder.as_markup()

def back_to_fav_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_fav"))
    return builder.as_markup()
    
