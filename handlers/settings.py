from aiogram import Router, F, types
from aiogram.enums import ParseMode
from motor.motor_asyncio import AsyncIOMotorClient
from os import getenv

from config import EMOJIS
from keyboards import (
    settings_inline_keyboard,
    language_selection_keyboard,
    notifications_keyboard,
    daily_reminder_keyboard,
    anime_prefs_keyboard,
    back_to_settings_keyboard
)

router = Router()
client = AsyncIOMotorClient(getenv("MONGO_URL"))
db = client['anicen_v2']
users_collection = db['users']

@router.message(F.text == "⚙️ Sozlamalar")
async def settings_main_handler(event: types.Message | types.CallbackQuery):
    text = (
        f"<tg-emoji emoji-id='{EMOJIS['settings']}'>⚙️</tg-emoji> <b>Sozlamalar bo‘limi</b>\n\n"
        f"Bot interfeysini o‘zingizga moslab sozlang."
    )
    if isinstance(event, types.Message):
        await event.answer(text, reply_markup=settings_inline_keyboard(), parse_mode=ParseMode.HTML)
    else:
        await event.message.edit_text(text, reply_markup=settings_inline_keyboard(), parse_mode=ParseMode.HTML)

# --- BILDIRISHNOMALAR (TUGMALARNI ISHLATISH) ---
@router.callback_query(F.data == "sett_notify")
async def settings_notify_handler(callback: types.CallbackQuery):
    user_data = await users_collection.find_one({"user_id": callback.from_user.id})
    is_on = user_data.get("notify", True)
    status_text = "YOQILGAN" if is_on else "O‘CHIRILGAN"
    
    await callback.message.edit_text(
        f"🔔 <b>Bildirishnomalar: {status_text}</b>",
        reply_markup=notifications_keyboard(),
        parse_mode=ParseMode.HTML
    )

@router.callback_query(F.data.startswith("set_notify_"))
async def toggle_notify(callback: types.CallbackQuery):
    action = callback.data.split("_")[-1]
    status = True if action == "on" else False
    await users_collection.update_one({"user_id": callback.from_user.id}, {"$set": {"notify": status}})
    await callback.answer(f"Bildirishnomalar o'zgartirildi!")
    await settings_notify_handler(callback)

# --- KUNLIK ESLATMA ---
@router.callback_query(F.data == "daily_reminder_menu")
async def daily_reminder_menu(callback: types.CallbackQuery):
    user_data = await users_collection.find_one({"user_id": callback.from_user.id})
    is_on = user_data.get("daily_reminder", True)
    status = "✅" if is_on else "❌"
    await callback.message.edit_text(f"📅 <b>Kunlik eslatma: {status}</b>", reply_markup=daily_reminder_keyboard())

@router.callback_query(F.data.startswith("set_daily_"))
async def toggle_daily(callback: types.CallbackQuery):
    action = callback.data.split("_")[-1]
    status = True if action == "on" else False
    await users_collection.update_one({"user_id": callback.from_user.id}, {"$set": {"daily_reminder": status}})
    await callback.answer("Eslatma sozlandi!")
    await daily_reminder_menu(callback)

@router.callback_query(F.data == "back_to_settings")
async def back_to_settings(callback: types.CallbackQuery):
    await settings_main_handler(callback)
