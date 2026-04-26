import os
from pymongo import MongoClient

client = MongoClient(os.getenv("MONGO_URL"))
db = client["anicen"]

users = db["users"]

def get_user(user_id):
    return users.find_one({"user_id": user_id})

def create_user(data):
    users.insert_one(data)

def update_user(user_id, data):
    users.update_one({"user_id": user_id}, {"$set": data})

def add_favorite(user_id, anime):
    users.update_one(
        {"user_id": user_id},
        {"$addToSet": {"favorites": anime}}
    )

def get_favorites(user_id):
    user = get_user(user_id)
    return user.get("favorites", []) if user else []

def find_users_with_favorite(title):
    return users.find({"favorites.title": title})
