from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types

def main_menu_keyboard():
    """Asosiy menyu tugmalari"""
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="🔍 Anime qidirish", callback_data="search"),
        types.InlineKeyboardButton(text="📂 Janrlar", callback_data="genres")
    )
    builder.row(
        types.InlineKeyboardButton(text="⭐ Tanlanganlar", callback_data="favs"),
        types.InlineKeyboardButton(text="🎲 Tasodifiy anime", callback_data="random")
    )
    builder.row(
        types.InlineKeyboardButton(text="🏆 Top-100", callback_data="top100"),
        types.InlineKeyboardButton(text="⚙️ Sozlamalar", callback_data="settings")
    )
    builder.row(
        types.InlineKeyboardButton(text="👤 Profil", callback_data="profile"),
        types.InlineKeyboardButton(text="📅 Kunlik ball", callback_data="daily_bonus")
    )
    return builder.as_markup()

def profile_keyboard():
    """Profil ichidagi tugmalar"""
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🪙 Ballarni sarflash", callback_data="spend"))
    builder.row(types.InlineKeyboardButton(text="👥 Do'stlarni taklif qilish", callback_data="referral"))
    builder.row(types.InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_main"))
    return builder.as_markup()

def start_registration_keyboard():
    """Birinchi marta kirganda chiqadigan tugmalar"""
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🆕 ADK YARATISH", callback_data="gen_adk"))
    builder.row(types.InlineKeyboardButton(text="🔑 MENDA ADK BOR", callback_data="have_adk"))
    return builder.as_markup()
    
