from aiogram import Router, F, types
from motor.motor_asyncio import AsyncIOMotorClient
from os import getenv
from keyboards import (
    settings_inline_keyboard, 
    notifications_keyboard, 
    daily_reminder_keyboard,
    language_selection_keyboard  # <--- Buni qo'shdik
)

router = Router()
db = AsyncIOMotorClient(getenv("MONGO_URL"))['anicen_v2']
users_collection = db['users']

# 1. SOZLAMALAR ASOSIY MENYUSI
@router.message(F.text == "⚙️ Sozlamalar")
async def settings_main(message: types.Message):
    await message.answer("⚙️ Sozlamalar menyusi", reply_markup=settings_inline_keyboard())

# 2. TILNI TANLASH MENYUSINI OCHISH
@router.callback_query(F.data == "sett_lang")
async def lang_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "🌐 Interfeys tilini tanlang / Выберите язык интерфейса:", 
        reply_markup=language_selection_keyboard()
    )

# 3. TILNI BAZADA YANGILASH
@router.callback_query(F.data.startswith("set_lang_"))
async def set_user_language(callback: types.CallbackQuery):
    lang_code = callback.data.split("_")[-1] 
    
    await users_collection.update_one(
        {"user_id": callback.from_user.id},
        {"$set": {"lang": lang_code}}
    )
    
    msg_text = {
        "uz": "Til o'zgartirildi! ✅",
        "ru": "Язык изменен! ✅",
        "en": "Language changed! ✅",
        "jp": "言語が変更されました! ✅"
    }
    
    await callback.answer(msg_text.get(lang_code, "✅"), show_alert=True)
    # Menyuni yangilash (Message ob'ekti orqali)
    await settings_main(callback.message)

# 4. BILDIRISHNOMALAR MENYUSI
@router.callback_query(F.data == "sett_notify")
async def notify_menu(callback: types.CallbackQuery):
    await callback.message.edit_text("🔔 Bildirishnomalarni sozlang:", reply_markup=notifications_keyboard())

@router.callback_query(F.data.startswith("set_notify_"))
async def toggle_notify(callback: types.CallbackQuery):
    status = True if callback.data == "set_notify_on" else False
    await users_collection.update_one({"user_id": callback.from_user.id}, {"$set": {"notify": status}})
    await callback.answer("O'zgartirildi!")
    await notify_menu(callback)

# 5. KUNLIK ESLATMA
@router.callback_query(F.data == "daily_reminder_menu")
async def daily_menu(callback: types.CallbackQuery):
    await callback.message.edit_text("📅 Kunlik eslatma:", reply_markup=daily_reminder_keyboard())

@router.callback_query(F.data.startswith("set_daily_"))
async def toggle_daily(callback: types.CallbackQuery):
    status = True if callback.data == "set_daily_on" else False
    await users_collection.update_one({"user_id": callback.from_user.id}, {"$set": {"daily_reminder": status}})
    await callback.answer("Eslatma sozlandi!")
    await daily_menu(callback)

# 6. ORQAGA QAYTISH
@router.callback_query(F.data == "back_to_settings")
async def back_settings(callback: types.CallbackQuery):
    await callback.message.edit_text("⚙️ Sozlamalar menyusi", reply_markup=settings_inline_keyboard())
