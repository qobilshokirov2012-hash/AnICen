import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from motor.motor_asyncio import AsyncIOMotorClient

# O'zing yaratgan fayllarni chaqiramiz
from config import BOT_TOKEN, MONGO_URL
from handlers import start, sevimlilar, profile, settings

async def main():
    # Logging sozlamalari (Railway loglarida ko'rinib turishi uchun)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout
    )

    # MongoDB-ga ulanish
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.anicen_v2 # Ma'lumotlar bazasi nomi

    # Bot obyekti
    bot = Bot(
        token=BOT_TOKEN, 
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Dispatcher
    dp = Dispatcher()

    # Bazani barcha handlerlarga yetkazish (middleware o'rniga oddiyroq yo'li)
    dp["db"] = db

    # Routerlarni ulaymiz (Shu yerda start xabari ulanadi)
    dp.include_router(start.router)
    dp.include_router(sevimlilar.router)
    dp.include_router(profile.router)
    dp.include_router(settings.router)

    # Botni ishga tushiramiz
    logging.info("Bot ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot to'xtatildi!")
      
