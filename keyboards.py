from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

# --- 1. ASOSIY REPLAY MENYU ---
def main_reply_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="🌟 Sevimlilar"), KeyboardButton(text="👤 Profil"))
    builder.row(KeyboardButton(text="🛒 Do‘kon"), KeyboardButton(text="⚙️ Sozlamalar"))
    return builder.as_markup(resize_keyboard=True)

# --- 2. SOZLAMALAR MENYUSI ---
def settings_inline_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🌐 Tilni o'zgartirish", callback_data="sett_lang"))
    builder.add(InlineKeyboardButton(text="🔔 Bildirishnomalar", callback_data="sett_notify"))
    builder.adjust(1)
    return builder.as_markup()

# --- 3. TILNI TANLASH ---
def language_selection_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="set_lang_uz"))
    builder.add(InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_lang_ru"))
    builder.add(InlineKeyboardButton(text="🇬🇧 English", callback_data="set_lang_en"))
    builder.add(InlineKeyboardButton(text="🇯🇵 日本語", callback_data="set_lang_jp"))
    builder.adjust(2)
    return builder.as_markup()

# --- 4. BILDIRISHNOMALAR ---
def notifications_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🔔 Yoqish", callback_data="set_notify_on"))
    builder.add(InlineKeyboardButton(text="🔕 O'chirish", callback_data="set_notify_off"))
    builder.row(InlineKeyboardButton(text="📅 Kunlik eslatma", callback_data="daily_reminder_menu"))
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_settings"))
    builder.adjust(2, 1, 1)
    return builder.as_markup()

# --- 5. KUNLIK ESLATMA ---
def daily_reminder_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="✅ Yoqish", callback_data="set_daily_on"))
    builder.add(InlineKeyboardButton(text="❌ O'chirish", callback_data="set_daily_off"))
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="sett_notify"))
    builder.adjust(2, 1)
    return builder.as_markup()

# --- 6. PROFIL VA DO'KON ---
def profile_inline_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🛒 Do'konga kirish", callback_data="open_shop"))
    return builder.as_markup()

def back_to_shop_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="⬅️ Do'konga qaytish", callback_data="open_shop"))
    return builder.as_markup()
    
