from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types

def main_menu_keyboard():
    builder = InlineKeyboardBuilder()
    
    # 1-qator
    builder.row(
        types.InlineKeyboardButton(text="🔍 Qidirish", callback_data="search"),
        types.InlineKeyboardButton(text="🏆 Top", callback_data="top100")
    )
    
    # 2-qator
    builder.row(
        types.InlineKeyboardButton(text="🎬 Epizodlar", callback_data="episodes")
    )
    
    # 3-qator 
    builder.row(
        types.InlineKeyboardButton(text="🌟 Sevimlilar", callback_data="favs"),
        types.InlineKeyboardButton(text="🎲 Tasodifiy Anime", callback_data="random")
    )
    
    # 4-qator
    builder.row(
        types.InlineKeyboardButton(text="👤 Profil", callback_data="cmd_adk"),
        types.InlineKeyboardButton(text="⚙️ Sozlamalar", callback_data="settings")
    )
    
    return builder.as_markup()
    
