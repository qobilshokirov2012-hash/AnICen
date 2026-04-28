import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from motor.motor_asyncio import AsyncIOMotorClient

# O'zing yaratgan fayllardan import qilish
from config import BOT_TOKEN, MONGO_URL
from handlers import start, sevimlilar, profile, settings

async def main():
    # Railway loglarida xatolarni ko'rish uchun logging sozlamasi
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout
    )

    # 1. MongoDB ulanishi
    if not MONGO_URL:
        logging.error("MONGO_URL topilmadi! Railway Variables-ni tekshiring.")
        return
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.anicen_v2  # Ma'lumotlar bazasi nomi

    # 2. Bot obyekti (HTML formatlash bilan)
    if not BOT_TOKEN:
        logging.error("BOT_TOKEN topilmadi! Railway Variables-ni tekshiring.")
        return

    bot = Bot(
        token=BOT_TOKEN, 
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # 3. Dispatcher
    dp = Dispatcher()

    # Bazani barcha handlerlarga uzatish (Middleware kabi ishlaydi)
    dp["db"] = db

    # 4. Routerlarni (fayllarni) ulash
    dp.include_router(start.router)
    dp.include_router(sevimlilar.router)
    dp.include_router(profile.router)
    dp.include_router(settings.router)

    # Botni ishga tushirish
    try:
        logging.info("Bot muvaffaqiyatli ishga tushdi!")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot to'xtatildi!")
        
