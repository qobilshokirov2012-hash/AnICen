from config import EMOJIS

# Emoji formatlash funksiyasi
def get_emoji(emoji_id: str) -> str:
    return f'<tg-emoji emoji_id="{emoji_id}"></tg-emoji>'

# Yangi foydalanuvchi uchun
START_NEW_USER = (
    f"{get_emoji(EMOJIS['naruto'])} Assalomu alaykum, {{first_name}}!\n\n"
    f"{get_emoji(EMOJIS['wave'])} Anime botga xush kelibsiz!\n\n"
    f"{get_emoji(EMOJIS['id'])} Sizning ID: <code>{{user_id}}</code>\n"
    f"{get_emoji(EMOJIS['date'])} Boshlangan vaqt: {{start_time}}\n\n"
    f"{get_emoji(EMOJIS['tv'])} Bu bot orqali siz:\n"
    f"— Anime qidirishingiz {get_emoji(EMOJIS['search'])}\n"
    f"— Sevimlilarga qo‘shishingiz {get_emoji(EMOJIS['favorite'])}\n"
    f"— Profilingizni boshqarishingiz {get_emoji(EMOJIS['profile2'])}\n"
    f"— Til va sozlamalarni o‘zgartirishingiz {get_emoji(EMOJIS['settings'])}\n\n"
    f"{get_emoji(EMOJIS['question'])} Boshlash uchun quyidagi tugmalardan birini tanlang:"
)

# Qayta kirgan foydalanuvchi uchun
START_EXISTING_USER = (
    f"{get_emoji(EMOJIS['gojo'])} Yana ko‘rishganimizdan xursandman, {{first_name}}!\n\n"
    f"{get_emoji(EMOJIS['id'])} ID: <code>{{user_id}}</code>\n"
    f"{get_emoji(EMOJIS['date'])} Oxirgi kirish: {{last_start}}\n\n"
    f"{get_emoji(EMOJIS['tv'])} Anime dunyosi sizni kutmoqda!\n"
    f"Quyidagi tugmalardan foydalaning!"
)

# Bot ichida turib start bosilganda
ALREADY_IN_BOT = (
    f"{get_emoji(EMOJIS['kakashi'])} Siz allaqachon botdasiz!\n\n"
    f"{get_emoji(EMOJIS['id'])} ID: <code>{{user_id}}</code>\n"
    f"{get_emoji(EMOJIS['date'])} So‘nggi faollik: {{last_start}}\n\n"
    f"{get_emoji(EMOJIS['search'])} Anime qidirishni davom ettiramizmi?"
)
