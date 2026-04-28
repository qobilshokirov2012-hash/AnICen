from aiogram import Router, types
from aiogram.filters import CommandStart
from datetime import datetime
import strings
from keyboards import get_main_menu # Yangi menyu

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message, db):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    current_time = datetime.now().strftime("%d.%m.%Y | %H:%M")
    
    user = await db.users.find_one({"user_id": user_id})
    
    # Reply menyuni tayyorlab olamiz
    main_menu = get_main_menu()
    
    if not user:
        await db.users.insert_one({
            "user_id": user_id,
            "first_name": first_name,
            "joined_at": current_time,
            "last_active": current_time,
            "lang": "uz"
        })
        text = strings.START_NEW_USER.format(
            first_name=first_name, 
            user_id=user_id, 
            start_time=current_time
        )
        await message.answer(text, reply_markup=main_menu)
    else:
        last_start = user.get("last_active", "Noma'lum")
        
        await db.users.update_one(
            {"user_id": user_id}, 
            {"$set": {"last_active": current_time, "first_name": first_name}}
        )
        
        text = strings.START_EXISTING_USER.format(
            first_name=first_name, 
            user_id=user_id, 
            last_start=last_start
        )
        await message.answer(text, reply_markup=main_menu)
        
