from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from config import EMOJIS

def get_main_menu():
    # Tugmalarni sening xohishing bo'yicha tartiblaymiz
    kb = [
        [
            KeyboardButton(text=f"🔍 Qidiruv"),
            KeyboardButton(text=f"❤️ Sevimlilar")
        ],
        [
            KeyboardButton(text=f"👤 Profil"),
            KeyboardButton(text=f"⚙️ Sozlamalar")
        ]
    ]
    return ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True, # Tugmalarni ixcham qiladi
        input_field_placeholder="Bo'limni tanlang..."
    )
    
