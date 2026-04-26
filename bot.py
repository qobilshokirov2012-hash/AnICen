from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🔍 Anime qidirish", callback_data="search"),
        InlineKeyboardButton("📂 Janrlar", callback_data="genres"),
        InlineKeyboardButton("⭐ Tanlanganlar", callback_data="favorites"),
        InlineKeyboardButton("🎲 Tasodifiy anime", callback_data="random"),
        InlineKeyboardButton("🏆 Top-100", callback_data="top"),
        InlineKeyboardButton("⚙️ Sozlamalar", callback_data="settings"),
        InlineKeyboardButton("➕ ADK yaratish", callback_data="create_adk"),
        InlineKeyboardButton("🔑 Menda ADK bor", callback_data="have_adk"),
    )
    return kb
