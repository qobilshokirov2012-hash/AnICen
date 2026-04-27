# --- START HANDLER ---
@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    
    # Bazada tekshirish (motor-asyncio)
    user_data = await users_collection.find_one({"user_id": user_id})
    if not user_data:
        await users_collection.insert_one({
            "user_id": user_id,
            "first_name": first_name,
            "points": 50,
            "favorites": [],
            "join_date": datetime.now()
        })

    # DIQQAT: <tg-emoji> ichida faqat bitta belgi yoki bo'sh joy bo'lishi shart!
    welcome_text = (
        f"<tg-emoji emoji-id='6028282982744202450'>✨</tg-emoji> <b>╔═══ ANICEN ═══╗</b>\n"
        f"   Anime dunyosiga xush kelibsiz\n"
        f"<tg-emoji emoji-id='6028282982744202450'>✨</tg-emoji> <b>╚═════════════════╝</b>\n\n"
        f"<tg-emoji emoji-id='5784885558287276809'>👋</tg-emoji> Salom, <b>{first_name}</b>!\n\n"
        f"Siz bu yerda:\n"
        f"<tg-emoji emoji-id='5332724926216428039'>👤</tg-emoji> Profil ochasiz\n"
        f"<tg-emoji emoji-id='5348282577662778261'>🔍</tg-emoji> Anime qidirasiz\n"
        f"<tg-emoji emoji-id='6325682031741109665'>🎬</tg-emoji> Epizodlarni tomosha qilasiz\n"
        f"<tg-emoji emoji-id='5361979846845014099'>🌟</tg-emoji> Sevimlilarni saqlaysiz\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"<tg-emoji emoji-id='5352743837502545676'>🔥</tg-emoji> Trend animelar sizni kutmoqda!\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"<tg-emoji emoji-id='5332722143077613679'>⚡</tg-emoji> Boshlash uchun tugmani tanlang:"
    )

    await message.answer(welcome_text, reply_markup=main_menu_keyboard(), parse_mode=ParseMode.HTML)
    
