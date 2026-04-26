import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from database import db
import keyboards as kb

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- HANDLERLAR ---

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    username = message.from_user.username
    
    args = message.text.split()
    if len(args) > 1 and args[1].isdigit():
        referrer_id = int(args[1])
        if referrer_id != user_id:
            await db.update_points(referrer_id, 50)
            try:
                await bot.send_message(referrer_id, "🎉 Taklifingiz uchun +50 ball berildi!")
            except: pass

    user_data = await db.get_user(user_id)
    if not user_data:
        await db.add_user(user_id, username, full_name)
        await message.answer(f"Salom, {full_name}! 👋\nAnICen botga xush kelibsiz!", reply_markup=kb.get_start_buttons())
    else:
        await db.update_points(user_id, 10)
        adk = user_data.get('adk_id', "Mavjud emas")
        await message.answer(f"Xush kelibsiz! 👋\nID: {user_id}\nADK: {adk}", reply_markup=kb.get_main_menu())

@dp.callback_query(F.data == "settings")
async def profile_handler(callback: types.CallbackQuery):
    await callback.answer()
    user = await db.get_user(callback.from_user.id)
    if not user: return
    
    # Xavfsiz olish (KeyError oldini olish)
    f_name = user.get('full_name', "Noma'lum")
    lvl = user.get('level', "Yangi boshlovchi 🌱")
    pts = user.get('points', 0)
    w_count = user.get('watched_count', 0)
    
    text = (f"👤 Profil: {f_name}\n"
            f"🎖 Daraja: {lvl}\n"
            f"🪙 Ballar: {pts}\n"
            f"🎬 Ko'rilgan: {w_count}")
    try:
        await callback.message.edit_text(text, reply_markup=kb.profile_buttons())
    except: pass

@dp.callback_query(F.data == "back_to_main")
async def back_main(callback: types.CallbackQuery):
    await callback.answer()
    try:
        await callback.message.edit_text("Asosiy menyu:", reply_markup=kb.get_main_menu())
    except: pass

@dp.callback_query(F.data == "shop")
async def shop_menu(callback: types.CallbackQuery):
    await callback.answer()
    user = await db.get_user(callback.from_user.id)
    pts = user.get('points', 0)
    await callback.message.edit_text(f"🛒 Do'kon\nBalingiz: {pts} 🪙", reply_markup=kb.shop_buttons())

@dp.callback_query(F.data == "buy_no_ads")
async def buy_ads(callback: types.CallbackQuery):
    success = await db.spend_points(callback.from_user.id, 200, "no_ads")
    if success:
        await callback.answer("✅ Reklamasiz rejim yoqildi!", show_alert=True)
        await shop_menu(callback)
    else:
        await callback.answer("❌ Ballar yetarli emas!", show_alert=True)

@dp.callback_query(F.data == "leaderboard")
async def show_top(callback: types.CallbackQuery):
    await callback.answer()
    top_list = await db.get_top_users()
    text = "🏆 Top-10 Foydalanuvchilar:\n\n"
    for i, u in enumerate(top_list, 1):
        name = u.get('full_name', "Noma'lum")
        p = u.get('points', 0)
        text += f"{i}. {name} - {p} 🪙\n"
    
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data="settings"))
    await callback.message.edit_text(text, reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("fav_"))
async def fav_pagination(callback: types.CallbackQuery):
    await callback.answer()
    page = int(callback.data.split("_")[1])
    favs = await db.get_favorites(callback.from_user.id)
    
    if not favs:
        await callback.message.edit_text("⭐ Tanlanganlar bo'sh!", reply_markup=kb.get_main_menu())
        return

    limit = 5
    total_pages = (len(favs) + limit - 1) // limit
    start = (page - 1) * limit
    builder = InlineKeyboardBuilder()
    for item in favs[start:start+limit]:
        builder.row(InlineKeyboardButton(text=f"🎬 {item.get('anime_name', 'Anime')}", callback_data=f"info_{item.get('anime_id')}"))
    
    nav = []
    if page > 1: nav.append(InlineKeyboardButton(text="⬅️", callback_data=f"fav_{page-1}"))
    nav.append(InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data="none"))
    if page < total_pages: nav.append(InlineKeyboardButton(text="➡️", callback_data=f"fav_{page+1}"))
    
    builder.row(*nav)
    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_main"))
    await callback.message.edit_text("⭐ Tanlanganlar:", reply_markup=builder.as_markup())

@dp.callback_query(F.data == "none")
async def empty_callback(callback: types.CallbackQuery):
    await callback.answer()

@dp.callback_query(F.data == "referral")
async def referral_handler(callback: types.CallbackQuery):
    await callback.answer()
    me = await bot.get_me()
    link = f"https://t.me/{me.username}?start={callback.from_user.id}"
    await callback.message.answer(f"👥 Havolangiz: `{link}`\nHar bir do'st uchun +50 ball!", parse_mode="Markdown")

# --- MAIN ---
async def main():
    logging.basicConfig(level=logging.INFO)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except:
        pass
    
