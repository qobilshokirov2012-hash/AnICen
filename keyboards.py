from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram import types

# --- ASOSIY REPLY MENYU (Pastdagi knopkalar) ---
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

# --- PROFIL INLINE TUGMASI ---
def profile_inline_keyboard():
    builder = InlineKeyboardBuilder()
    # Faqat "Do‘kon" tugmasi qoladi (Eski ballar tizimi o'chirildi)
    builder.row(types.InlineKeyboardButton(text="🛒 Do‘kon", callback_data="open_shop"))
    return builder.as_markup()

# --- DO'KON MENYUSI (Ryo va Rank tizimi) ---
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
    # Profilga qaytish tugmasi (back_to_profile handleriga moslangan)
    builder.row(types.InlineKeyboardButton(text="❌ Orqaga", callback_data="back_to_profile"))
    return builder.as_markup()

# --- DO'KON ICHIDAN ORQAGA QAYTISH ---
def back_to_shop_keyboard():
    builder = InlineKeyboardBuilder()
    # Ma'lumotlar bo'limidan yana do'konga qaytaradi
    builder.row(types.InlineKeyboardButton(text="⬅️ Orqaga", callback_data="open_shop"))
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

# --- ANIME SAHIFASI (🌟 Sevimlilar toggle) ---
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
    
