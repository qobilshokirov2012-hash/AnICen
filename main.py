import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

# Handlerlarni import qilish
# Diqqat: 'handlers' papkangiz ichida __init__.py fayli bo'lishi shart!
try:
    from handlers import start, profile, settings, sevimlilar
except ImportError as e:
    print(f"Import xatosi: {e}")
    sys.exit(1)

# LOGGING - Railway loglarida xatoni ko'rish uchun muhim
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)

async def main():
    # Tokenni Railway Variables'dan oladi
    TOKEN = getenv("BOT_TOKEN")
    
    if not TOKEN:
        logging.error("BOT_TOKEN topilmadi! Railway Variables bo'limini tekshiring.")
        return

    # Bot obyektini yaratish
    bot = Bot(
        token=TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    dp = Dispatcher()

    # ROUTERLARNI ULASH
    # Tartib muhim: avval start, keyin qolganlari
    dp.include_router(start.router)
    dp.include_router(profile.router)
    dp.include_router(settings.router)
    dp.include_router(sevimlilar.router)

    logging.info("Bot ishga tushmoqda... ✅")

    try:
        # Eski xabarlarni o'chirib yuborish (webhook tozalash)
        await bot.delete_webhook(drop_pending_updates=True)
        # Pollingni boshlash
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Bot ishlashida xatolik: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot to'xtatildi! 🛑")
      
