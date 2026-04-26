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

# --- HANDLERLAR BOSHLANISHI ---

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    username = message.from_user.username
    
    # Referal tizimi
    args = message.text.split()
    if len(args) > 1 and args[1].isdigit():
        referrer_id = int(args[1])
        if referrer_id != user_id:
            await db.update_points(referrer_id, 50)
            try:
                await bot.send_message(referrer_id, "🎉 Taklifingiz uchun +50 ball berildi!")
            except:
                pass

    user_data = await db.get_user(user_id)
    if not user_data:
        await db.add_user(user_id, username, full_name)
        welcome_text = (
            f"Salom, {full_name}! 👋\n"
            f"Dunyodagi eng qiziqarli animelar olamiga xush kelibsiz!\n"
            f"Pastdagi tugmalardan birini tanlang:"
        )
        await message.answer(welcome_text, reply_markup=kb.get_start_buttons())
    else:
        await db.update_points(user_id, 10)
        re_text = (
            f"Sizni yana koʻrganimizdan xursandmiz! {full_name}👋\n"
            f"🆔 ID: {user_id}\n"
            f"🔑 ADK: {user_data.get('adk_id', 'Mavjud emas')}\n\n"
            f"Davom etish uchun menyudan kerakli boʻlimni tanlang:"
        )
        await message.answer(re_text, reply_markup=kb.get_main_menu())

@dp.callback_query(F.data == "settings")
async def profile_handler(callback: types.CallbackQuery):
    await callback.answer()
    user = await db.get_user(callback.from_user.id)
    
    if not user:
        await callback.message.answer("Profilingiz topilmadi. Iltimos, /start bosing.")
        return

    # KeyError oldini olish uchun .get() ishlatamiz
    f_name = user.get('full_name', callback.from_user.full_name)
    lvl = user.get('level', 'Yangi boshlovchi 🌱')
    pts = user.get('points', 0)
    w_count = user.get('watched_count', 0)
    a_id = user.get('adk_id', 'Mavjud emas')

    profile_text = (
        f"👤 Foydalanuvchi Profili\n\n"
        f"👤 Ism: {f_name}\n"
        f"🎖 Daraja: {lvl}\n"
        f"🪙 Jami ballar: {pts} 🪙\n"
        f"🎬 Ko‘rilgan animelar: {w_count} ta\n"
        f"🔑 ADK: {a_id}"
    )
    
    try:
        await callback.message.edit_text(profile_text, reply_markup=kb.profile_buttons())
    except Exception:
        pass

@dp.callback_query(F.data == "back_to_main")
async def back_main(callback: types.CallbackQuery):
    await callback.answer()
    try:
        await callback.message.edit_text("Asosiy menyu:", reply_markup=kb.get_main_menu())
    except Exception:
        pass

@dp.callback_query(F.data == "shop")
async def shop_menu(callback: types.CallbackQuery):
    await callback.answer()
    user = await db.get_user(callback.from_user.id)
    pts = user.get('points', 0)
    text = f"🛒 Do'kon\nBalingiz: {pts} 🪙\n\nSotib olish uchun tugmani bosing:"
    try:
        await callback.message.edit_text(text, reply_markup=kb.shop_buttons())
    except Exception:
        pass

@dp.callback_query(F.data == "buy_no_ads")
async def buy_ads(callback: types.CallbackQuery):
    success = await db.spend_points(callback.from_user.id, 200, "no_ads")
    if success:
        await callback.answer("✅ Reklamasiz rejim faollashdi!", show_alert=True)
        await shop_menu(callback)
    else:
        await callback.answer("❌ Ballar yetarli emas!", show_alert=True)

@dp.callback_query(F.data == "leaderboard")
async def show_top(callback: types.CallbackQuery):
    await callback.answer()
    top_list = await db.get_top_users()
    text = "🏆 Top-10 Foydalanuvchilar:\n\n"
    for i, u in enumerate(top_list, 1):
        name = u.get('full_name', 'Noma'lum')
        p = u.get('points', 0)
        text += f"{i}. {name} - {p} 🪙\n"
    
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data="settings"))
    try:
        await callback.message.edit_text(text, reply_markup=builder.as_markup())
    except Exception:
        pass

@dp.callback_query(F.data.startswith("fav_"))
async def fav_pagination(callback: types.CallbackQuery):
    await callback.answer()
    page = int(callback.data.split("_")[1])
    favs = await db.get_favorites(callback.from_user.id)
    
    if not favs:
        try:
            await callback.message.edit_text("⭐ Tanlanganlar ro'yxati bo'sh!", reply_markup=kb.get_main_menu())
        except Exception:
            pass
        return

    limit = 5
    total_pages = (len(favs) + limit - 1) // limit
    start = (page - 1) * limit
    end = start + limit
    
    builder = InlineKeyboardBuilder()
    for item in favs[start:end]:
        anime_id = str(item.get('anime_id', '0'))
        anime_name = item.get('anime_name', 'Noma'lum')
        builder.row(InlineKeyboardButton(text=f"🎬 {anime_name}", callback_data=f"info_{anime_id}"))
    
    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton(text="⬅️", callback_data=f"fav_{page-1}"))
    nav.append(InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data="none"))
    if page < total_pages:
        nav.append(InlineKeyboardButton(text="➡️", callback_data=f"fav_{page+1}"))
    
    builder.row(*nav)
    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_main"))
    
    try:
        await callback.message.edit_text("⭐ Tanlangan animelar ro'yxati:", reply_markup=builder.as_markup())
    except Exception:
        pass

@dp.callback_query(F.data == "none")
async def empty_callback(callback: types.CallbackQuery):
    await callback.answer()

@dp.callback_query(F.data == "referral")
async def referral_handler(callback: types.CallbackQuery):
    await callback.answer()
    bot_info = await bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start={callback.from_user.id}"
    text = (
        f"👥 Do'stlarni taklif qiling va ball ishlang!\n\n"
        f"Sizning havolangiz:\n`{ref_link}`\n\n"
        f"Har bir do'stingiz uchun +50 ball beriladi."
    )
    await callback.message.answer(text, parse_mode="Markdown")

# --- ASOSIY ISHGA TUSHIRISH QISMI ---

async def main():
    logging.basicConfig(level=logging.INFO)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot to'xtatildi")
