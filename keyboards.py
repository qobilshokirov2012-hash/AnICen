from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_start_buttons():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔍 Anime qidirish", callback_data="search"),
                InlineKeyboardButton(text="📂 Janrlar", callback_data="genres"))
    builder.row(InlineKeyboardButton(text="⭐ Tanlanganlar", callback_data="fav_1"),
                InlineKeyboardButton(text="🎲 Tasodifiy anime", callback_data="random"))
    builder.row(InlineKeyboardButton(text="🏆 Top-100", callback_data="top_100"),
                InlineKeyboardButton(text="⚙️ Sozlamalar", callback_data="settings"))
    return builder.as_markup()

def get_main_menu():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔍 Qidirish", callback_data="search"),
                InlineKeyboardButton(text="⭐ Tanlanganlar", callback_data="fav_1"))
    builder.row(InlineKeyboardButton(text="⚙️ Sozlamalar", callback_data="settings"))
    return builder.as_markup()

def profile_buttons():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🛒 Do'kon", callback_data="shop"),
                InlineKeyboardButton(text="👥 Taklif qilish", callback_data="referral"))
    builder.row(InlineKeyboardButton(text="📊 Reyting", callback_data="leaderboard"),
                InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_main"))
    return builder.as_markup()

def shop_buttons():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🚫 Reklamasiz (200 🪙)", callback_data="buy_no_ads"))
    builder.row(InlineKeyboardButton(text="🔙 Profilga", callback_data="settings"))
    return builder.as_markup()
    
