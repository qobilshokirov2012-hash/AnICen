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
    
def favorites_inline_keyboard():
    builder = InlineKeyboardBuilder()
    # 1-qator: Orqaga va Keyingi
    builder.row(
        types.InlineKeyboardButton(text="⬅️ Orqaga", callback_data="fav_prev"),
        types.InlineKeyboardButton(text="➡️ Keyingi", callback_data="fav_next")
    )
    # 2-qator: Haqida va Oxirgi qo'shilganlar
    builder.row(
        types.InlineKeyboardButton(text="Haqida? ↓", callback_data="fav_about"),
        types.InlineKeyboardButton(text="Oxirgi qo'shilganlar", callback_data="fav_recent")
    )
    return builder.as_markup()

def anime_item_keyboard(anime_id, is_favorite=False):
    """Anime sahifasidagi toggle tugma"""
    builder = InlineKeyboardBuilder()
    if is_favorite:
        text = "❌ Sevimlilardan olib tashlash"
        callback = f"rem_fav_{anime_id}"
    else:
        text = "🌟 Sevimlilarga qo'shish"
        callback = f"add_fav_{anime_id}"
    
    builder.row(types.InlineKeyboardButton(text=text, callback_data=callback))
    return builder.as_markup()
    
# keyboards.py fayliga qo'shing

def profile_inline_keyboard():
    builder = InlineKeyboardBuilder()
    # Ballarni sarflash bo'limiga o'tish
    builder.row(
        types.InlineKeyboardButton(text="🪙 Ballarni sarflash", callback_data="spend_points")
    )
    # Ballar qanday yig'ilishi haqida ma'lumot
    builder.row(
        types.InlineKeyboardButton(text="❓ Ballar haqida", callback_data="about_points")
    )
    return builder.as_markup()

def spend_points_inline_keyboard():
    builder = InlineKeyboardBuilder()
    # Do'kon elementlari (misol tariqasida)
    builder.row(
        types.InlineKeyboardButton(text="🚫 Reklamani o'chirish", callback_data="buy_no_ads")
    )
    builder.row(
        types.InlineKeyboardButton(text="✨ Maxsus profil", callback_data="buy_premium_profile")
    )
    # Orqaga profilga qaytish
    builder.row(
        types.InlineKeyboardButton(text="⬅️ Profilga qaytish", callback_data="back_to_profile")
    )
    return builder.as_markup()
    
