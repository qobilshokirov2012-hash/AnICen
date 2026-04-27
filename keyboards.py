from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

def main_reply_keyboard():
    builder = ReplyKeyboardBuilder()
    # Bildirishnomalar bu yerdan olib tashlandi, chunki u Sozlamalar ichida bor
    builder.row(KeyboardButton(text="🌟 Sevimlilar"), KeyboardButton(text="👤 Profil"))
    builder.row(KeyboardButton(text="🛒 Do‘kon"), KeyboardButton(text="⚙️ Sozlamalar"))
    return builder.as_markup(resize_keyboard=True)

def notifications_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🔔 Yoqish", callback_data="set_notify_on"))
    builder.add(InlineKeyboardButton(text="🔕 O'chirish", callback_data="set_notify_off"))
    builder.row(InlineKeyboardButton(text="📅 Kunlik eslatma", callback_data="daily_reminder_menu"))
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_settings"))
    builder.adjust(2, 1, 1)
    return builder.as_markup()

def daily_reminder_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="✅ Yoqish", callback_data="set_daily_on"))
    builder.add(InlineKeyboardButton(text="❌ O'chirish", callback_data="set_daily_off"))
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="sett_notify"))
    builder.adjust(2, 1)
    return builder.as_markup()
    
