import sqlite3
import aiosqlite
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import asyncio


class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path

    async def init_database(self):
        """Ma'lumotlar bazasini yaratish"""
        async with aiosqlite.connect(self.db_path) as db:
            # Foydalanuvchilar jadvali
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Kinolar jadvali
            await db.execute('''
                CREATE TABLE IF NOT EXISTS movies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    file_id TEXT NOT NULL,
                    file_id_4k TEXT,
                    views INTEGER DEFAULT 0,
                    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 4K maydonini mavjud jadvalga qo'shish (agar yo'q bo'lsa)
            try:
                await db.execute('ALTER TABLE movies ADD COLUMN file_id_4k TEXT')
                await db.commit()
            except:
                pass  # Ustun allaqachon mavjud

            # Kanallar jadvali
            await db.execute('''
                CREATE TABLE IF NOT EXISTS channels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    channel_id INTEGER UNIQUE NOT NULL,
                    channel_name TEXT NOT NULL,
                    channel_username TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Kino ko'rilishlar jadvali
            await db.execute('''
                CREATE TABLE IF NOT EXISTS movie_views (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    movie_code TEXT,
                    view_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (movie_code) REFERENCES movies (code)
                )
            ''')

            # Xabar statistikasi jadvali
            await db.execute('''
                CREATE TABLE IF NOT EXISTS broadcast_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id INTEGER,
                    total_users INTEGER,
                    successful_sends INTEGER,
                    failed_sends INTEGER,
                    broadcast_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Premium obuna sozlamalari jadvali
            await db.execute('''
                CREATE TABLE IF NOT EXISTS premium_settings (
                    id INTEGER PRIMARY KEY,
                    price_1month INTEGER DEFAULT 5000,
                    price_3months INTEGER DEFAULT 12000,
                    price_6months INTEGER DEFAULT 20000,
                    price_12months INTEGER DEFAULT 35000,
                    description TEXT DEFAULT 'Premium obuna: Majburiy obuna talab etilmaydi',
                    is_enabled BOOLEAN DEFAULT FALSE,
                    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Foydalanuvchilar premium obunalari jadvali
            await db.execute('''
                CREATE TABLE IF NOT EXISTS user_premium (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE NOT NULL,
                    start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_date TIMESTAMP NOT NULL,
                    subscription_type TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')

            # Premium obuna to'lovlari jadvali
            await db.execute('''
                CREATE TABLE IF NOT EXISTS premium_payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    amount INTEGER,
                    subscription_type TEXT,
                    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'pending',
                    receipt_message_id INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')

            # To'lov kartalari jadvali
            await db.execute('''
                CREATE TABLE IF NOT EXISTS payment_cards (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    card_number TEXT NOT NULL,
                    card_holder_name TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # To'lov tekshiruvlari jadvali
            await db.execute('''
                CREATE TABLE IF NOT EXISTS payment_verifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    payment_id INTEGER,
                    receipt_message_id INTEGER,
                    status TEXT DEFAULT 'pending',
                    admin_id INTEGER,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed_date TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (payment_id) REFERENCES premium_payments (id)
                )
            ''')

            # Bot adminlari jadvali
            await db.execute('''
                CREATE TABLE IF NOT EXISTS bot_admins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE NOT NULL,
                    username TEXT,
                    first_name TEXT,
                    permissions TEXT DEFAULT 'basic',
                    added_by INTEGER,
                    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (added_by) REFERENCES users (user_id)
                )
            ''')

            await db.commit()

    # Foydalanuvchilar bilan ishlash
    async def add_user(self, user_id: int, username: str = None, first_name: str = None, last_name: str = None):
        """Yangi foydalanuvchi qo'shish"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT OR REPLACE INTO users (user_id, username, first_name, last_name, last_activity)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, username, first_name, last_name, datetime.now()))
            await db.commit()

    async def get_user(self, user_id: int) -> Optional[Dict]:
        """Foydalanuvchi ma'lumotlarini olish"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            row = await cursor.fetchone()
            if row:
                return {
                    'user_id': row[0],
                    'username': row[1],
                    'first_name': row[2],
                    'last_name': row[3],
                    'join_date': row[4],
                    'is_active': row[5],
                    'last_activity': row[6]
                }
            return None

    async def update_user_activity(self, user_id: int):
        """Foydalanuvchi faolligini yangilash"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                UPDATE users SET last_activity = ? WHERE user_id = ?
            ''', (datetime.now(), user_id))
            await db.commit()

    async def get_users_count(self) -> int:
        """Barcha foydalanuvchilar sonini olish"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('SELECT COUNT(*) FROM users')
            result = await cursor.fetchone()
            return result[0] if result else 0

    async def get_today_users_count(self) -> int:
        """Bugungi yangi foydalanuvchilar soni"""
        today = datetime.now().date()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                'SELECT COUNT(*) FROM users WHERE DATE(join_date) = ?',
                (today,)
            )
            result = await cursor.fetchone()
            return result[0] if result else 0

    async def get_week_users_count(self) -> int:
        """7 kunlik yangi foydalanuvchilar soni"""
        week_ago = datetime.now() - timedelta(days=7)
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                'SELECT COUNT(*) FROM users WHERE join_date >= ?',
                (week_ago,)
            )
            result = await cursor.fetchone()
            return result[0] if result else 0

    async def get_active_users_count(self) -> int:
        """Faol foydalanuvchilar soni (oxirgi 24 soatda)"""
        day_ago = datetime.now() - timedelta(hours=24)
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                'SELECT COUNT(*) FROM users WHERE last_activity >= ?',
                (day_ago,)
            )
            result = await cursor.fetchone()
            return result[0] if result else 0

    async def get_all_users(self) -> List[int]:
        """Barcha foydalanuvchilar ID larini olish"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('SELECT user_id FROM users WHERE is_active = TRUE')
            result = await cursor.fetchall()
            return [row[0] for row in result]

    # Kinolar bilan ishlash
    async def add_movie(self, code: str, title: str, file_id: str, file_id_4k: str = None) -> bool:
        """Yangi kino qo'shish"""
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute('''
                    INSERT INTO movies (code, title, file_id, file_id_4k)
                    VALUES (?, ?, ?, ?)
                ''', (code, title, file_id, file_id_4k))
                await db.commit()
                return True
            except sqlite3.IntegrityError:
                return False
    async def update_movie_4k(self, movie_id: int, file_id_4k: str) -> bool:
        """Kinoga 4K video qo'shish"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                UPDATE movies SET file_id_4k = ? WHERE id = ?
            ''', (file_id_4k, movie_id))
            await db.commit()
            return cursor.rowcount > 0

    async def get_movie_by_code(self, code: str) -> Optional[Dict]:
        """Kod bo'yicha kino olish"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('SELECT * FROM movies WHERE code = ?', (code,))
            row = await cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'code': row[1],
                    'title': row[2],
                    'file_id': row[3],
                    'file_id_4k': row[4],
                    'views': row[5],
                    'added_date': row[6]
                }
            return None

    async def get_all_movies(self) -> List[Dict]:
        """Barcha kinolar ro'yxati"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('SELECT * FROM movies ORDER BY added_date DESC')
            rows = await cursor.fetchall()
            return [
                {
                    'id': row[0],
                    'code': row[1],
                    'title': row[2],
                    'file_id': row[3],
                    'views': row[4],
                    'added_date': row[5]
                }
                for row in rows
            ]

    async def delete_movie(self, movie_id: int) -> bool:
        """Kinoni o'chirish"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('DELETE FROM movies WHERE id = ?', (movie_id,))
            await db.commit()
            return cursor.rowcount > 0

    async def increment_movie_views(self, code: str, user_id: int):
        """Kino ko'rilishlar sonini oshirish"""
        async with aiosqlite.connect(self.db_path) as db:
            # Ko'rilishlar sonini oshirish
            await db.execute('''
                UPDATE movies SET views = views + 1 WHERE code = ?
            ''', (code,))
            
            # Ko'rilish tarixini saqlash
            await db.execute('''
                INSERT INTO movie_views (user_id, movie_code)
                VALUES (?, ?)
            ''', (user_id, code))
            
            await db.commit()

    async def get_movies_count(self) -> int:
        """Barcha kinolar soni"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('SELECT COUNT(*) FROM movies')
            result = await cursor.fetchone()
            return result[0] if result else 0

    async def get_top_movies(self, limit: int = 10) -> List[Dict]:
        """Eng ko'p ko'rilgan kinolar"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                SELECT * FROM movies 
                ORDER BY views DESC 
                LIMIT ?
            ''', (limit,))
            rows = await cursor.fetchall()
            return [
                {
                    'id': row[0],
                    'code': row[1],
                    'title': row[2],
                    'file_id': row[3],
                    'views': row[4],
                    'added_date': row[5]
                }
                for row in rows
            ]

    # Kanallar bilan ishlash
    async def add_channel(self, channel_id: int, channel_name: str, channel_username: str = None) -> bool:
        """Yangi kanal qo'shish"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT INTO channels (channel_id, channel_name, channel_username)
                    VALUES (?, ?, ?)
                ''', (channel_id, channel_name, channel_username))
                await db.commit()
                return True
        except sqlite3.IntegrityError:
            return False

    async def get_all_channels(self) -> List[Dict]:
        """Barcha kanallar ro'yxati"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('SELECT * FROM channels WHERE is_active = TRUE')
            rows = await cursor.fetchall()
            return [
                {
                    'id': row[0],
                    'channel_id': row[1],
                    'channel_name': row[2],
                    'channel_username': row[3],
                    'is_active': row[4],
                    'added_date': row[5]
                }
                for row in rows
            ]

    async def delete_channel(self, channel_id: int) -> bool:
        """Kanalni o'chirish"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('DELETE FROM channels WHERE id = ?', (channel_id,))
            await db.commit()
            return cursor.rowcount > 0

    async def get_channels_count(self) -> int:
        """Barcha kanallar soni"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('SELECT COUNT(*) FROM channels WHERE is_active = TRUE')
            result = await cursor.fetchone()
            return result[0] if result else 0

    # Statistika
    async def save_broadcast_stats(self, message_id: int, total_users: int, successful_sends: int, failed_sends: int):
        """Broadcast statistikasini saqlash"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT INTO broadcast_stats (message_id, total_users, successful_sends, failed_sends)
                VALUES (?, ?, ?, ?)
            ''', (message_id, total_users, successful_sends, failed_sends))
            await db.commit()

    async def get_total_broadcasts(self) -> int:
        """Umumiy broadcast xabarlari soni"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('SELECT SUM(successful_sends) FROM broadcast_stats')
            result = await cursor.fetchone()
            return result[0] if result and result[0] else 0

    # Premium obuna bilan ishlash
    async def init_premium_settings(self):
        """Premium sozlamalarini boshlang'ich holatda yaratish"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT OR IGNORE INTO premium_settings (id, price_1month, price_3months, price_6months, price_12months)
                VALUES (1, 5000, 12000, 20000, 35000)
            ''')
            await db.commit()

    async def get_premium_settings(self) -> Dict:
        """Premium sozlamalarini olish"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('SELECT * FROM premium_settings WHERE id = 1')
            row = await cursor.fetchone()
            if row:
                return {
                    'price_1month': row[1],
                    'price_3months': row[2], 
                    'price_6months': row[3],
                    'price_12months': row[4],
                    'description': row[5],
                    'is_enabled': bool(row[6])
                }
            return {
                'price_1month': 5000,
                'price_3months': 12000,
                'price_6months': 20000,
                'price_12months': 35000,
                'description': 'Premium obuna: Majburiy obuna talab etilmaydi',
                'is_enabled': False
            }

    async def update_premium_prices(self, price_1m: int, price_3m: int, price_6m: int, price_12m: int):
        """Premium narxlarni yangilash"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                UPDATE premium_settings 
                SET price_1month = ?, price_3months = ?, price_6months = ?, price_12months = ?, updated_date = ?
                WHERE id = 1
            ''', (price_1m, price_3m, price_6m, price_12m, datetime.now()))
            await db.commit()

    async def update_premium_description(self, description: str):
        """Premium tavsifni yangilash"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                UPDATE premium_settings 
                SET description = ?, updated_date = ?
                WHERE id = 1
            ''', (description, datetime.now()))
            await db.commit()

    async def toggle_premium_status(self, is_enabled: bool):
        """Premium holatni yoqish/o'chirish"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                UPDATE premium_settings 
                SET is_enabled = ?, updated_date = ?
                WHERE id = 1
            ''', (is_enabled, datetime.now()))
            await db.commit()

    async def add_user_premium(self, user_id: int, subscription_type: str, months: int):
        """Foydalanuvchiga premium obuna qo'shish"""
        start_date = datetime.now()
        end_date = start_date + timedelta(days=30 * months)
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT OR REPLACE INTO user_premium (user_id, start_date, end_date, subscription_type, is_active)
                VALUES (?, ?, ?, ?, TRUE)
            ''', (user_id, start_date, end_date, subscription_type))
            await db.commit()

    async def check_user_premium(self, user_id: int) -> bool:
        """Foydalanuvchining premium obunasini tekshirish"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                SELECT end_date FROM user_premium 
                WHERE user_id = ? AND is_active = TRUE AND end_date > ?
            ''', (user_id, datetime.now()))
            result = await cursor.fetchone()
            return bool(result)

    async def get_premium_users_count(self) -> int:
        """Premium foydalanuvchilar sonini olish"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                SELECT COUNT(*) FROM user_premium 
                WHERE is_active = TRUE AND end_date > ?
            ''', (datetime.now(),))
            result = await cursor.fetchone()
            return result[0] if result else 0

    async def get_user_completed_payments(self, user_id: int) -> List[Dict]:
        """Foydalanuvchining faqat tasdiqlangan to'lovlarini olish"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                SELECT pp.amount, pp.subscription_type, pp.payment_date
                FROM premium_payments pp
                WHERE pp.user_id = ? AND pp.status = 'completed'
                ORDER BY pp.payment_date DESC
            ''', (user_id,))
            rows = await cursor.fetchall()
            return [{
                'amount': row[0],
                'subscription_type': row[1],
                'payment_date': row[2]
            } for row in rows]

    async def check_premium_expiry(self, user_id: int) -> Dict:
        """Premium muddatini tekshirish va qolgan kunlarni hisoblash"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                SELECT end_date, subscription_type FROM user_premium 
                WHERE user_id = ? AND is_active = TRUE AND end_date > ?
                ORDER BY end_date DESC LIMIT 1
            ''', (user_id, datetime.now()))
            result = await cursor.fetchone()
            
            if result:
                end_date = datetime.fromisoformat(result[0])
                remaining_days = (end_date - datetime.now()).days
                return {
                    'has_premium': True,
                    'end_date': end_date,
                    'remaining_days': remaining_days,
                    'subscription_type': result[1],
                    'is_expiring_soon': remaining_days <= 3  # 3 kun qolganda ogohlantirish
                }
            return {
                'has_premium': False,
                'end_date': None,
                'remaining_days': 0,
                'subscription_type': None,
                'is_expiring_soon': False
            }

    async def get_expiring_users(self) -> List[Dict]:
        """Muddati tugash arafasidagi foydalanuvchilarni olish (3 kun qolgan)"""
        async with aiosqlite.connect(self.db_path) as db:
            three_days_later = datetime.now() + timedelta(days=3)
            cursor = await db.execute('''
                SELECT up.user_id, up.end_date, up.subscription_type, u.username, u.first_name
                FROM user_premium up
                JOIN users u ON up.user_id = u.user_id
                WHERE up.is_active = TRUE AND up.end_date BETWEEN ? AND ?
                ORDER BY up.end_date ASC
            ''', (datetime.now(), three_days_later))
            rows = await cursor.fetchall()
            
            return [{
                'user_id': row[0],
                'end_date': row[1],
                'subscription_type': row[2],
                'username': row[3],
                'first_name': row[4]
            } for row in rows]

    async def remove_user_premium(self, user_id: int):
        """Foydalanuvchining premium obunasini o'chirish (muddati tugaganda)"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                UPDATE user_premium 
                SET is_active = FALSE 
                WHERE user_id = ? AND is_active = TRUE
            ''', (user_id,))
            await db.commit()

    async def add_premium_payment(self, user_id: int, amount: int, subscription_type: str, receipt_message_id: int = None):
        """Premium to'lovni qo'shish"""
        async with aiosqlite.connect(self.db_path) as db:
            if receipt_message_id is not None:
                # Chek message ID bilan
                cursor = await db.execute('''
                    INSERT INTO premium_payments (user_id, amount, subscription_type, status, receipt_message_id)
                    VALUES (?, ?, ?, 'pending', ?)
                ''', (user_id, amount, subscription_type, receipt_message_id))
            else:
                # Chek message ID siz
                cursor = await db.execute('''
                    INSERT INTO premium_payments (user_id, amount, subscription_type, status)
                    VALUES (?, ?, ?, 'pending')
                ''', (user_id, amount, subscription_type))
            await db.commit()
            return cursor.lastrowid

    # Karta boshqaruvi
    async def add_payment_card(self, card_number: str, card_holder_name: str):
        """To'lov kartasini qo'shish"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT INTO payment_cards (card_number, card_holder_name)
                VALUES (?, ?)
            ''', (card_number, card_holder_name))
            await db.commit()

    async def get_active_cards(self):
        """Faol kartalarni olish"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                SELECT * FROM payment_cards WHERE is_active = TRUE ORDER BY added_date DESC
            ''')
            rows = await cursor.fetchall()
            return [
                {
                    'id': row[0],
                    'card_number': row[1],
                    'card_holder_name': row[2],
                    'is_active': row[3],
                    'added_date': row[4]
                }
                for row in rows
            ]

    async def deactivate_all_cards(self):
        """Barcha kartalarni faol bo'lmagan holatga o'tkazish"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('UPDATE payment_cards SET is_active = FALSE')
            await db.commit()

    async def activate_card(self, card_id: int):
        """Kartani faollashtirish"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('UPDATE payment_cards SET is_active = TRUE WHERE id = ?', (card_id,))
            await db.commit()

    async def get_card_by_id(self, card_id: int):
        """ID bo'yicha kartani olish"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                SELECT * FROM payment_cards WHERE id = ?
            ''', (card_id,))
            row = await cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'card_number': row[1],
                    'card_holder_name': row[2],
                    'is_active': row[3],
                    'added_date': row[4]
                }
            return None

    # To'lov tekshiruvi
    async def add_payment_verification(self, user_id: int, payment_id: int, receipt_message_id: int):
        """To'lov tekshiruvini qo'shish"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                INSERT INTO payment_verifications (user_id, payment_id, receipt_message_id, status)
                VALUES (?, ?, ?, 'pending')
            ''', (user_id, payment_id, receipt_message_id))
            await db.commit()
            return cursor.lastrowid

    async def get_pending_payments(self):
        """Kutilayotgan to'lovlarni olish"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                SELECT pv.id, pv.user_id, pv.payment_id, pv.receipt_message_id, pv.created_date,
                       pp.amount, pp.subscription_type, u.first_name, u.username
                FROM payment_verifications pv
                JOIN premium_payments pp ON pv.payment_id = pp.id
                JOIN users u ON pv.user_id = u.user_id
                WHERE pv.status = 'pending'
                ORDER BY pv.created_date DESC
            ''')
            rows = await cursor.fetchall()
            return [
                {
                    'verification_id': row[0],
                    'user_id': row[1],
                    'payment_id': row[2],
                    'receipt_message_id': row[3],
                    'created_date': row[4],
                    'amount': row[5],
                    'subscription_type': row[6],
                    'first_name': row[7],
                    'username': row[8]
                }
                for row in rows
            ]

    async def approve_payment(self, verification_id: int, admin_id: int):
        """To'lovni tasdiqlash"""
        async with aiosqlite.connect(self.db_path) as db:
            # Verification ni yangilash
            await db.execute('''
                UPDATE payment_verifications 
                SET status = 'approved', admin_id = ?, processed_date = ?
                WHERE id = ?
            ''', (admin_id, datetime.now(), verification_id))
            
            # Payment ni yangilash
            await db.execute('''
                UPDATE premium_payments 
                SET status = 'completed'
                WHERE id = (SELECT payment_id FROM payment_verifications WHERE id = ?)
            ''', (verification_id,))
            
            await db.commit()

    async def reject_payment(self, verification_id: int, admin_id: int):
        """To'lovni rad etish"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                UPDATE payment_verifications 
                SET status = 'rejected', admin_id = ?, processed_date = ?
                WHERE id = ?
            ''', (admin_id, datetime.now(), verification_id))
            
            await db.execute('''
                UPDATE premium_payments 
                SET status = 'rejected'
                WHERE id = (SELECT payment_id FROM payment_verifications WHERE id = ?)
            ''', (verification_id,))
            
            await db.commit()

    async def get_payment_by_verification_id(self, verification_id: int):
        """Verification ID bo'yicha to'lov ma'lumotlarini olish"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                SELECT pv.user_id, pp.amount, pp.subscription_type
                FROM payment_verifications pv
                JOIN premium_payments pp ON pv.payment_id = pp.id
                WHERE pv.id = ?
            ''', (verification_id,))
            row = await cursor.fetchone()
            if row:
                return {
                    'user_id': row[0],
                    'amount': row[1],
                    'subscription_type': row[2]
                }
            return None

    # Admin boshqaruvi
    async def add_admin(self, user_id: int, username: str = None, first_name: str = None, permissions: str = 'basic', added_by: int = None):
        """Yangi admin qo'shish"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT INTO bot_admins (user_id, username, first_name, permissions, added_by)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, username, first_name, permissions, added_by))
                await db.commit()
                return True
        except sqlite3.IntegrityError:
            return False

    async def remove_admin(self, user_id: int):
        """Adminni o'chirish"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                UPDATE bot_admins SET is_active = FALSE WHERE user_id = ?
            ''', (user_id,))
            await db.commit()
            return cursor.rowcount > 0

    async def get_all_admins(self):
        """Barcha adminlar ro'yxati"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                SELECT user_id, username, first_name, permissions, added_date, is_active
                FROM bot_admins
                ORDER BY added_date DESC
            ''')
            rows = await cursor.fetchall()
            return [{
                'user_id': row[0],
                'username': row[1],
                'first_name': row[2],
                'permissions': row[3],
                'added_date': row[4],
                'is_active': row[5]
            } for row in rows]

    async def check_admin_permissions(self, user_id: int):
        """Admin huquqlarini tekshirish"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                SELECT permissions, is_active FROM bot_admins WHERE user_id = ?
            ''', (user_id,))
            row = await cursor.fetchone()
            if row and row[1]:  # is_active = True
                return row[0]  # permissions
            return None

    async def update_admin_permissions(self, user_id: int, permissions: str):
        """Admin huquqlarini yangilash"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                UPDATE bot_admins SET permissions = ? WHERE user_id = ? AND is_active = TRUE
            ''', (permissions, user_id))
            await db.commit()
            return cursor.rowcount > 0