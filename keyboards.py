from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types

def main_menu_keyboard():
    builder = InlineKeyboardBuilder()
    
    # 1-qator: Qidirish va Top
    builder.row(
        types.InlineKeyboardButton(text="🔍 Qidirish", callback_data="search"),
        types.InlineKeyboardButton(text="🏆 Top", callback_data="top100")
    )
    
    # 2-qator: Epizodlar
    builder.row(
        types.InlineKeyboardButton(text="🎬 Epizodlar", callback_data="episodes")
    )
    
    # 3-qator: Sevimlilar
    builder.row(
        types.InlineKeyboardButton(text="🔥 Sevimlilar", callback_data="favs")
    )
    
    # 4-qator: Profil va Sozlamalar
    builder.row(
        types.InlineKeyboardButton(text="👤 Profil", callback_data="profile"),
        types.InlineKeyboardButton(text="⚙️ Sozlamalar", callback_data="settings")
    )
    
    return builder.as_markup()
    
