from aiogram import Router, F, types
from motor.motor_asyncio import AsyncIOMotorClient
from os import getenv
from keyboards import settings_inline_keyboard, notifications_keyboard, daily_reminder_keyboard

router = Router()
db = AsyncIOMotorClient(getenv("MONGO_URL"))['anicen_v2']
users_collection = db['users']

@router.message(F.text == "⚙️ Sozlamalar")
async def settings_main(message: types.Message):
    await message.answer("⚙️ Sozlamalar menyusi", reply_markup=settings_inline_keyboard())

@router.callback_query(F.data == "sett_notify")
async def notify_menu(callback: types.CallbackQuery):
    await callback.message.edit_text("🔔 Bildirishnomalarni sozlang:", reply_markup=notifications_keyboard())

@router.callback_query(F.data.startswith("set_notify_"))
async def toggle_notify(callback: types.CallbackQuery):
    status = True if callback.data == "set_notify_on" else False
    await users_collection.update_one({"user_id": callback.from_user.id}, {"$set": {"notify": status}})
    await callback.answer("O'zgartirildi!")
    await notify_menu(callback)

@router.callback_query(F.data == "daily_reminder_menu")
async def daily_menu(callback: types.CallbackQuery):
    await callback.message.edit_text("📅 Kunlik eslatma:", reply_markup=daily_reminder_keyboard())

@router.callback_query(F.data.startswith("set_daily_"))
async def toggle_daily(callback: types.CallbackQuery):
    status = True if callback.data == "set_daily_on" else False
    await users_collection.update_one({"user_id": callback.from_user.id}, {"$set": {"daily_reminder": status}})
    await callback.answer("Eslatma sozlandi!")
    await daily_menu(callback)

@router.callback_query(F.data == "back_to_settings")
async def back_settings(callback: types.CallbackQuery):
    await callback.message.edit_text("⚙️ Sozlamalar menyusi", reply_markup=settings_inline_keyboard())
    
