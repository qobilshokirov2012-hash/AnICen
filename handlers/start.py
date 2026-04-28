from aiogram import Router, types
from aiogram.filters import CommandStart
from datetime import datetime
import strings
from keyboards import get_start_keyboard

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message, db): # db obyekti middleware orqali keladi deb faraz qilamiz
    user_id = message.from_user.id
    first_name = message.from_user.first_name
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
        text = strings.START_NEW_USER.format(
            first_name=first_name, 
            user_id=user_id, 
            start_time=current_time
        )
        await message.answer(text, reply_markup=get_start_keyboard(), parse_mode="HTML")
    else:
        # Eski foydalanuvchi
        last_start = user.get("last_active", "Noma'lum")
        
        # Oxirgi faollikni yangilaymiz
        await db.users.update_one(
            {"user_id": user_id}, 
            {"$set": {"last_active": current_time}}
        )
        
        # Bu yerda mantiq: Agar xabar o'chirib tashlanmagan bo'lsa "Alla qachon botdasiz" 
        # lekin har doim ham buni aniqlab bo'lmaydi, shuning uchun "Yana ko'rishganimizdan xursandman" varianti ketadi
        text = strings.START_EXISTING_USER.format(
            first_name=first_name, 
            user_id=user_id, 
            last_start=last_start
        )
        await message.answer(text, reply_markup=get_start_keyboard(), parse_mode="HTML")
        
