from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram import types

# --- ASOSIY REPLY MENYU ---
def main_reply_keyboard():
    builder = ReplyKeyboardBuilder()
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
    return builder.as_markup(resize_keyboard=True)

# --- ASOSIY INLINE MENYU (Agar kerak bo'lsa) ---
def main_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="🔍 Qidirish", callback_data="search"),
        types.InlineKeyboardButton(text="🏆 Top", callback_data="top100")
    )
    builder.row(types.InlineKeyboardButton(text="🎬 Epizodlar", callback_data="episodes"))
    builder.row(
        types.InlineKeyboardButton(text="🌟 Sevimlilar", callback_data="favs"),
        types.InlineKeyboardButton(text="🎲 Tasodifiy Anime", callback_data="random")
    )
    builder.row(
        types.InlineKeyboardButton(text="👤 Profil", callback_data="cmd_adk"),
        types.InlineKeyboardButton(text="⚙️ Sozlamalar", callback_data="settings")
    )
    return builder.as_markup()

# --- PROFIL VA BALLAR TIZIMI ---
def profile_inline_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🪙 Ballarni sarflash", callback_data="spend_points"))
    builder.row(types.InlineKeyboardButton(text="❓ Ballar haqida", callback_data="about_points"))
    return builder.as_markup()

def spend_points_inline_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🚫 Reklamani o'chirish", callback_data="buy_no_ads"))
    builder.row(types.InlineKeyboardButton(text="✨ Maxsus profil", callback_data="buy_premium_profile"))
    builder.row(types.InlineKeyboardButton(text="⬅️ Profilga qaytish", callback_data="back_to_profile"))
    return builder.as_markup()

# --- SEVIMLILAR BO'LIMI ---
def favorites_inline_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="⬅️ Orqaga", callback_data="fav_prev"),
        types.InlineKeyboardButton(text="➡️ Keyingi", callback_data="fav_next")
    )
    builder.row(
        types.InlineKeyboardButton(text="Haqida? ↓", callback_data="fav_about"),
        types.InlineKeyboardButton(text="Oxirgi qo'shilganlar", callback_data="fav_recent")
    )
    return builder.as_markup()

def back_to_fav_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_fav"))
    return builder.as_markup()

# --- ANIME SAHIFASI (TOGGLE) ---
def anime_item_keyboard(anime_id, is_favorite=False):
    builder = InlineKeyboardBuilder()
    if is_favorite:
        text = "❌ Sevimlilardan olib tashlash"
        callback = f"rem_fav_{anime_id}"
    else:
        text = "🌟 Sevimlilarga qo'shish"
        callback = f"add_fav_{anime_id}"
    builder.row(types.InlineKeyboardButton(text=text, callback_data=callback))
    return builder.as_markup()

# --- UMUMIY ORQAGA QAYTISH ---
def back_to_main_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_main"))
    return builder.as_markup()
    
# Profil ichidagi "Do'kon" tugmasi
def profile_inline_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🛒 Do‘kon", callback_data="open_shop"))
    return builder.as_markup()

# Do'kon menyusi
def shop_inline_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="⚔️ Kakashi (567 💴)", callback_data="buy_rank_kakashi"))
    builder.row(types.InlineKeyboardButton(text="🌸 Sakura (600 💴)", callback_data="buy_rank_sakura"))
    builder.row(types.InlineKeyboardButton(text="🗡 Sasuke (693 💴)", callback_data="buy_rank_sasuke"))
    builder.row(types.InlineKeyboardButton(text="🍥 Naruto (787 💴)", callback_data="buy_rank_naruto"))
    builder.row(
        types.InlineKeyboardButton(text="Ryo haqida?", callback_data="about_ryo"),
        types.InlineKeyboardButton(text="Daraja haqida?", callback_data="about_ranks")
    )
    builder.row(types.InlineKeyboardButton(text="❌ Orqaga", callback_data="back_to_profile"))
    return builder.as_markup()

# Faqat orqaga qaytish (Ryo/Daraja haqida bo'limidan do'konga)
def back_to_shop_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="⬅️ Orqaga", callback_data="open_shop"))
    return builder.as_markup()
    
