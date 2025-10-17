import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from aiogram.filters import CommandStart, Command

from config import BOT_TOKEN, DATABASE_PATH, ADMIN_IDS, WELCOME_TEXT
from database import Database


# Logging sozlash
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global database
db = None


async def main():
    """Asosiy funksiya"""
    global db
    
    # Bot va Dispatcher yaratish
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Ma'lumotlar bazasini yaratish
    db = Database(DATABASE_PATH)
    await db.init_database()
    
    # Test handlerlar
    @dp.message(CommandStart())
    async def start_command(message: Message):
        """Start komandasi handleri"""
        await db.add_user(
            user_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
        
        await db.update_user_activity(message.from_user.id)
        
        await message.answer(
            f"🎬 Assalomu alaykum, {message.from_user.first_name}!\n\n"
            "Kino kodini yuboring (masalan: 001)"
        )

    @dp.message(Command("admin"))
    async def admin_panel(message: Message):
        if message.from_user.id not in ADMIN_IDS:
            await message.answer("❌ Sizda admin huquqlari yo'q!")
            return
        
        stats = {
            'total_users': await db.get_users_count(),
            'total_movies': await db.get_movies_count(),
        }
        
        await message.answer(
            f"👑 **Admin Panel**\n\n"
            f"👥 Jami foydalanuvchilar: {stats['total_users']}\n"
            f"🎬 Jami kinolar: {stats['total_movies']}\n\n"
            f"Test version - asosiy funksiyalar ishlamoqda!"
        )

    @dp.message()
    async def handle_text(message: Message):
        """Matn xabarlarni qayta ishlash"""
        text = message.text
        if text and text.isalnum() and len(text) <= 10:
            # Bu kino kodi bo'lishi mumkin
            movie = await db.get_movie_by_code(text.upper())
            
            if movie:
                await message.answer_video(
                    video=movie['file_id'],
                    caption=f"🎬 {movie['title']}\n🆔 Kod: {movie['code']}"
                )
                await db.increment_movie_views(text.upper(), message.from_user.id)
            else:
                await message.answer(
                    "❌ Bu kod bilan kino topilmadi. Iltimos, to'g'ri kod kiriting."
                )
        else:
            await message.answer("Kino kodini yuboring (masalan: 001)")
    
    # Bot ma'lumotlarini olish
    bot_info = await bot.get_me()
    logger.info(f"Bot ishga tushdi: @{bot_info.username}")
    
    try:
        # Bot ishga tushirish
        await dp.start_polling(bot, skip_updates=True)
    except KeyboardInterrupt:
        logger.info("Bot to'xtatildi")
    finally:
        # Bot sessiyasini yopish
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())