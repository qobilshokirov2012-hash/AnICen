import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_name="anime_bot.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Foydalanuvchilar
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            points INTEGER DEFAULT 0,
            level TEXT DEFAULT 'Yangi boshlovchi 🌱',
            watched_count INTEGER DEFAULT 0,
            adk_id TEXT UNIQUE,
            joined_date TEXT
        )''')
        
        # Tanlanganlar (Paginatsiya uchun)
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            anime_id INTEGER,
            anime_name TEXT
        )''')
        self.conn.commit()

    def add_user(self, user_id, username, full_name):
        adk_id = f"ADK-{user_id}"
        date_now = datetime.now().strftime("%Y-%m-%d")
        self.cursor.execute("INSERT OR IGNORE INTO users (user_id, username, full_name, adk_id, joined_date) VALUES (?, ?, ?, ?, ?)",
                           (user_id, username, full_name, adk_id, date_now))
        self.conn.commit()

    def get_user(self, user_id):
        self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return self.cursor.fetchone()

    def update_points(self, user_id, amount):
        self.cursor.execute("UPDATE users SET points = points + ? WHERE user_id = ?", (amount, user_id))
        self.conn.commit()
        self.update_level(user_id)

    def update_level(self, user_id):
        user = self.get_user(user_id)
        points = user[3]
        level = "Yangi boshlovchi 🌱"
        if points >= 10000: level = "Anime Afsonasi 👑"
        elif points >= 5000: level = "Hokage 🔥"
        elif points >= 2000: level = "Shinobi ⚔️"
        elif points >= 500: level = "Naruto"
        self.cursor.execute("UPDATE users SET level = ? WHERE user_id = ?", (level, user_id))
        self.conn.commit()

    def get_favorites(self, user_id):
        self.cursor.execute("SELECT anime_name, anime_id FROM favorites WHERE user_id = ?", (user_id,))
        return self.cursor.fetchall()

db = Database()
      
