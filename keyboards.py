from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types

def main_menu_keyboard():
    builder = InlineKeyboardBuilder()
    
    # 1-qator: Qidirish va Top
    builder.row(
        types.InlineKeyboardButton(text="🔍 Qidirish", callback_data="search"),
        types.InlineKeyboardButton(text="🏆 Top", callback_data="top100")
    )
    
    # 2-qator: Epizodlar (To'liq qator)
    builder.row(
        types.InlineKeyboardButton(text="🎬 Epizodlar", callback_data="episodes")
    )
    
    # 3-qator: Sevimlilar (To'liq qator)
    builder.row(
        types.InlineKeyboardButton(text="🌟 Sevimlilar", callback_data="favs")
    )
    
    # 4-qator: Profil va Sozlamalar
    builder.row(
        types.InlineKeyboardButton(text="👤 Profil", callback_data="profile"),
        types.InlineKeyboardButton(text="⚙️ Sozlamalar", callback_data="settings")
    )
    
    return builder.as_markup()

def back_to_main_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_main"))
    return builder.as_markup()
    
