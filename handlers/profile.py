from aiogram import Router, F, types
import strings

router = Router()

@router.message(F.text == "👤 Profil")
async def show_profile(message: types.Message, db):
    user = await db.users.find_one({"user_id": message.from_user.id})
    # Bu yerda profil ma'lumotlarini chiqaramiz
    await message.answer(f"Sening profiling:\nID: {user['user_id']}")
  
