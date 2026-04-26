from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types

def main_menu_keyboard():
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
        types.InlineKeyboardButton(text="🤖 AI Chat", callback_data="ai_chat") # Yangi!
    )
    return builder.as_markup()

def profile_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🪙 Ballarni sarflash", callback_data="spend"))
    builder.row(types.InlineKeyboardButton(text="👥 Do'stlarni taklif qilish", callback_data="referral"))
    builder.row(types.InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_main"))
    return builder.as_markup()

def ai_characters_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="⚔️ Itachi Uchiha", callback_data="chat_itachi"),
        types.InlineKeyboardButton(text="🍵 Levi Ackerman", callback_data="chat_levi")
    )
    builder.row(types.InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_main"))
    return builder.as_markup()

def shop_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🚫 Reklamasiz rejim (200 🪙)", callback_data="buy_noads"))
    builder.row(types.InlineKeyboardButton(text="🎨 Ism rangini o'zgartirish (500 🪙)", callback_data="buy_color"))
    builder.row(types.InlineKeyboardButton(text="⬅️ Orqaga", callback_data="profile"))
    return builder.as_markup()
    
