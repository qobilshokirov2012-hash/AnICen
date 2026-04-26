import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

MONGO_URL = os.getenv("MONGO_URL")

class Database:
    def __init__(self):
        self.client = AsyncIOMotorClient(MONGO_URL)
        self.db = self.client.anime_bot_db
        self.users = self.db.users
        self.favorites = self.db.favorites

    async def add_user(self, user_id, username, full_name):
        adk_id = f"ADK-{user_id}"
        date_now = datetime.now().strftime("%Y-%m-%d")
        user_data = {
            "user_id": user_id,
            "username": username,
            "full_name": full_name,
            "points": 0,
            "level": "Yangi boshlovchi 🌱",
            "watched_count": 0,
            "adk_id": adk_id,
            "joined_date": date_now,
            "no_ads": False,      # Reklamasiz rejim
            "custom_font": None   # Profil bezagi
        }
        await self.users.update_one(
            {"user_id": user_id},
            {"$setOnInsert": user_data},
            upsert=True
        )

    async def get_user(self, user_id):
        return await self.users.find_one({"user_id": user_id})

    # --- BALLARNI BOSHQARISH ---
    async def update_points(self, user_id, amount):
        await self.users.update_one(
            {"user_id": user_id},
            {"$inc": {"points": amount}}
        )
        await self.check_level(user_id)

    async def spend_points(self, user_id, amount, service_name):
        user = await self.get_user(user_id)
        if user['points'] >= amount:
            await self.users.update_one(
                {"user_id": user_id},
                {"$inc": {"points": -amount}}
            )
            return True
        return False

    async def check_level(self, user_id):
        user = await self.get_user(user_id)
        p = user.get("points", 0)
        
        # Siz aytgan darajalar tizimi
        level = "Yangi boshlovchi 🌱"
        if p >= 10000: level = "Anime Afsonasi 👑"
        elif p >= 5000: level = "Hokage 🔥"
        elif p >= 2000: level = "Shinobi ⚔️"
        elif p >= 500: level = "Naruto"
        
        await self.users.update_one(
            {"user_id": user_id},
            {"$set": {"level": level}}
        )

    # --- TOP REYTING ---
    async def get_top_users(self):
        # Eng ko'p ball to'plagan 10 kishi
        cursor = self.users.find().sort("points", -1).limit(10)
        return await cursor.to_list(length=10)

db = Database()
        
