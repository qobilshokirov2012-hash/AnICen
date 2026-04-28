from aiogram import Router, types
from aiogram.filters import CommandStart
from datetime import datetime
import strings
from keyboards import get_start_keyboard

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message, db):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    # Hozirgi vaqtni sen xohlagan formatda olamiz
    current_time = datetime.now().strftime("%d.%m.%Y | %H:%M")
    
    # Foydalanuvchini bazadan qidiramiz
    user = await db.users.find_one({"user_id": user_id})
    
    if not user:
        # Yangi foydalanuvchi
        await db.users.insert_one({
            "user_id": user_id,
            "first_name": first_name,
            "joined_at": current_time,
            "last_active": current_time,
            "lang": "uz"
        })
        # strings.py ichidagi START_NEW_USER formatini to'ldiramiz
        text = strings.START_NEW_USER.format(
            first_name=first_name, 
            user_id=user_id, 
            start_time=current_time
        )
        await message.answer(text, reply_markup=get_start_keyboard())
    else:
        # Eski foydalanuvchi - oxirgi kirgan vaqtini saqlab olamiz
        last_start = user.get("last_active", "Noma'lum")
        
        # Bazada oxirgi faollikni yangilaymiz
        await db.users.update_one(
            {"user_id": user_id}, 
            {"$set": {"last_active": current_time, "first_name": first_name}} # Ismi o'zgargan bo'lsa yangilab qo'yadi
        )
        
        # Sening xohishing bo'yicha: qayta start bosilgandagi xabar
        text = strings.START_EXISTING_USER.format(
            first_name=first_name, 
            user_id=user_id, 
            last_start=last_start
        )
        await message.answer(text, reply_markup=get_start_keyboard())
        
