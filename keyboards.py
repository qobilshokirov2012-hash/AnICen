from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import EMOJIS

def get_start_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="🔍 Qidirish", switch_inline_query_current_chat=""),
            InlineKeyboardButton(text="❤️ Sevimlilar", callback_data="favorites")
        ],
        [
            InlineKeyboardButton(text="👤 Profil", callback_data="profile"),
            InlineKeyboardButton(text="⚙️ Sozlamalar", callback_data="settings")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
    
