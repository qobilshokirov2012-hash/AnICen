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
    
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram import types

def main_reply_keyboard():
    builder = ReplyKeyboardBuilder()
    
    # Tugmalarni rasm va siz aytgan tartibda joylashtiramiz
    builder.row(
        types.KeyboardButton(text="🔍 Qidirish"),
        types.KeyboardButton(text="🏆 Top")
    )
    builder.row(
        types.KeyboardButton(text="🎬 Epizodlar")
    )
    builder.row(
        types.KeyboardButton(text="🌟 Sevimlilar"),
        types.KeyboardButton(text="🎲 Tasodifiy Anime")
    )
    builder.row(
        types.KeyboardButton(text="👤 Profil"),
        types.KeyboardButton(text="⚙️ Sozlamalar")
    )
    
    # Menyuni ekranga moslashadigan va doimiy qilamiz
    return builder.as_markup(resize_keyboard=True)

# Inline orqaga qaytish tugmasi (xabarlar ichida qoladi)
def back_to_main_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_main"))
    return builder.as_markup()
    
