import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from database import db
import keyboards as kb

# Railway Environment Variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    username = message.from_user.username

    # MongoDB'ga foydalanuvchini qo'shish (asinxron)
    await db.add_user(user_id, username, full_name)
    user_data = await db.get_user(user_id)

    # Agar foydalanuvchi yangi bo'lsa (joined_date bugun bo'lsa)
    # Eslatma: joined_date mantiqini biroz soddalashtirdik
    text = (
        f"Salom, {full_name}! 👋\n"
        f"Dunyodagi eng qiziqarli animelar olamiga xush kelibsiz!\n"
        f"🆔 ID: {user_id}\n"
        f"🔑 ADK: {user_data.get('adk_id')}\n\n"
        f"Pastdagi tugmalardan birini tanlang:"
    )
    await message.answer(text, reply_markup=kb.get_start_buttons())

@dp.callback_query(F.data == "settings")
async def profile_callback(callback: types.CallbackQuery):
    user = await db.get_user(callback.from_user.id)
    profile_text = (
        f"👤 Foydalanuvchi Profili\n\n"
        f"Ism: {user['full_name']}\n"
        f"Daraja: {user['level']}\n"
        f"Jami ballar: {user['points']} 🪙\n"
        f"Ko‘rilgan animelar: {user['watched_count']} ta\n"
        f"ADK: {user['adk_id']}"
    )
    await callback.message.edit_text(profile_text, reply_markup=kb.profile_buttons())

@dp.callback_query(F.data.startswith("fav_"))
async def favorites_page(callback: types.CallbackQuery):
    page = int(callback.data.split("_")[1])
    favs = await db.get_favorites(callback.from_user.id)
    
    if not favs:
        await callback.answer("Sizda hali tanlangan animelar yo'q!", show_alert=True)
        return

    items_per_page = 5
    total_pages = (len(favs) + items_per_page - 1) // items_per_page
    start = (page - 1) * items_per_page
    end = start + items_per_page
    current_items = favs[start:end]

    builder = InlineKeyboardBuilder()
    for item in current_items:
        builder.row(InlineKeyboardButton(text=f"🎬 {item['anime_name']}", callback_data=f"view_{item['anime_id']}"))

    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton(text="⬅️", callback_data=f"fav_{page-1}"))
    nav.append(InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data="none"))
    if page < total_pages:
        nav.append(InlineKeyboardButton(text="➡️", callback_data=f"fav_{page+1}"))
    
    builder.row(*nav)
    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_main"))
    
    await callback.message.edit_text("⭐ Tanlangan animelar ro'yxati:", reply_markup=builder.as_markup())

@dp.callback_query(F.data == "back_to_main")
async def back_to_main_handler(callback: types.CallbackQuery):
    await callback.message.edit_text("Asosiy menyu:", reply_markup=kb.get_main_menu())

# Railway serveri uchun ishga tushirish funksiyasi
async def main():
    logging.basicConfig(level=logging.INFO)
    # Konfliktlarning oldini olish (Eski sessiyalarni tozalash)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
