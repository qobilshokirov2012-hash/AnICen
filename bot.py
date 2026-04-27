import asyncio
import logging
from datetime import datetime, timezone # UTC uchun
from os import getenv

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from motor.motor_asyncio import AsyncIOMotorClient

from keyboards import main_menu_keyboard
from config import EMOJIS # Emoji IDlarni import qilamiz

# --- KONFIGURATSIYA ---
BOT_TOKEN = getenv("BOT_TOKEN")
MONGO_URL = getenv("MONGO_URL")

client = AsyncIOMotorClient(MONGO_URL)
db = client['anicen_v2']
users_collection = db['users']

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    try:
        user_id = message.from_user.id
        first_name = message.from_user.first_name
        
        user_data = await users_collection.find_one({"user_id": user_id})
        
        if not user_data:
            # YANGI FOYDALANUVCHI UCHUN
            await users_collection.insert_one({
                "user_id": user_id,
                "first_name": first_name,
                "points": 50,
                "favorites": [],
                "join_date": datetime.now(timezone.utc) # Tavsiya: UTC vaqt
            })
            
            text = (
                f"<b>╔═══ ANICEN ═══╗</b>\n"
                f"   Anime dunyosiga xush kelibsiz\n"
                f"<b>╚═════════════════╝</b>\n\n"
                f"<tg-emoji emoji-id='{EMOJIS['welcome']}'>👋</tg-emoji> Salom yangi qahramon, <b>{first_name}</b>!\n\n"
                f"Sizga start bonus sifatida 50 🪙 berildi. Keling, sarguzashtni boshlaymiz!\n\n"
                f"⚡ Boshlash uchun tugmani tanlang:"
            )
        else:
            # MAVJUD FOYDALANUVCHI UCHUN (Shaxsiy xabar)
            text = (
                f"<b>╔═══ ANICEN ═══╗</b>\n"
                f"   Sizni yana ko'rganimizdan xursandmiz!\n"
                f"<b>╚═════════════════╝</b>\n\n"
                f"<tg-emoji emoji-id='{EMOJIS['welcome']}'>👋</tg-emoji> Qaytib kelganingiz bilan, <b>{first_name}</b>!\n\n"
                f"Bugun qanday anime ko'ramiz? Sevimlilar ro'yxatingiz yangilanishini kutyapti.\n\n"
                f"⚡ Davom etish uchun tanlang:"
            )

        await message.answer(text, reply_markup=main_menu_keyboard(), parse_mode=ParseMode.HTML)

    except Exception as e:
        logging.error(f"Start buyrug'ida xatolik: {e}")
        await message.answer("Tizimda kichik nosozlik yuz berdi. Birozdan so'ng qayta urinib ko'ring! 🛠")

# --- ISHGA TUSHIRISH ---
async def main():
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as e:
        logging.critical(f"Botni ishga tushirishda xato: {e}")

if __name__ == "__main__":
    asyncio.run(main())
    
