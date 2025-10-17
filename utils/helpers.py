from aiogram import Bot
from typing import List
import asyncio
import logging


async def check_user_subscription(bot: Bot, user_id: int, channels: List[dict], db = None) -> bool:
    """Foydalanuvchining kanallarga obunasini tekshirish"""
    # Premium obunani tekshirish
    if db:
        premium_settings = await db.get_premium_settings()
        if premium_settings['is_enabled']:
            has_premium = await db.check_user_premium(user_id)
            if has_premium:
                return True  # Premium foydalanuvchi majburiy obunadan ozod
    
    # Oddiy obuna tekshiruvi
    for channel in channels:
        try:
            channel_id = channel['channel_id']
            member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
            
            # Foydalanuvchi obuna bo'lmagan yoki ban qilingan bo'lsa
            if member.status in ['left', 'kicked']:
                return False
                
        except Exception as e:
            logging.error(f"Kanal {channel_id} ni tekshirishda xatolik: {e}")
            # Xatolik bo'lsa, obuna bo'lmagan deb hisoblaymiz
            return False
    
    return True


def format_number(number: int) -> str:
    """Sonlarni formatlash (1000 -> 1K)"""
    if number >= 1000000:
        return f"{number/1000000:.1f}M"
    elif number >= 1000:
        return f"{number/1000:.1f}K"
    else:
        return str(number)


def escape_markdown(text: str) -> str:
    """Markdown belgilarini escape qilish"""
    chars_to_escape = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in chars_to_escape:
        text = text.replace(char, f'\\{char}')
    return text


def format_movie_info(movie: dict) -> str:
    """Kino ma'lumotlarini formatlash"""
    return f"""
🎬 **{movie['title']}**
🆔 Kod: `{movie['code']}`
👁‍🗨 Ko'rishlar: {format_number(movie['views'])}
📅 Qo'shilgan: {movie['added_date'][:10]}
    """.strip()


def format_statistics(stats: dict) -> str:
    """Statistikani formatlash"""
    return f"""
📊 **Bot Statistikasi**

👥 **Foydalanuvchilar:**
• Jami: {format_number(stats.get('total_users', 0))}
• Bugun qo'shilgan: {format_number(stats.get('today_users', 0))}
• 7 kunlik: {format_number(stats.get('week_users', 0))}
• Faol: {format_number(stats.get('active_users', 0))}

🎬 **Kinolar:**
• Jami kinolar: {format_number(stats.get('total_movies', 0))}
• Jami ko'rishlar: {format_number(stats.get('total_views', 0))}

📢 **Kanallar:**
• Jami kanallar: {format_number(stats.get('total_channels', 0))}

📩 **Xabarlar:**
• Yuborilgan xabarlar: {format_number(stats.get('total_broadcasts', 0))}

👑 **Adminlar:**
• Adminlar soni: {format_number(stats.get('total_admins', 0))}
    """.strip()


async def send_movie_to_base_channel(bot: Bot, base_channel_id, movie_code: str, movie_title: str, file_id: str) -> tuple:
    """Kinoni baza kanalga yuborish"""
    try:
        caption = f"🎬 {movie_title}\n🆔 Kod: {movie_code}"
        
        # Avval bot kanalda admin ekanini tekshiramiz
        try:
            bot_member = await bot.get_chat_member(chat_id=base_channel_id, user_id=bot.id)
            if bot_member.status not in ['administrator', 'creator']:
                return False, "Bot kanalda admin emas"
        except Exception as check_error:
            return False, f"Kanalni tekshirishda xatolik: {check_error}"
        
        # Video yuborish
        message = await bot.send_video(
            chat_id=base_channel_id,
            video=file_id,
            caption=caption
        )
        
        return True, f"Muvaffaqiyatli yuborildi (Message ID: {message.message_id})"
        
    except Exception as e:
        error_msg = f"Baza kanalga yuborishda xatolik: {e}"
        logging.error(error_msg)
        return False, error_msg


async def broadcast_message(bot: Bot, user_ids: List[int], text: str = None, photo: str = None, video: str = None) -> tuple:
    """Barcha foydalanuvchilarga xabar yuborish"""
    successful = 0
    failed = 0
    
    for user_id in user_ids:
        try:
            if photo:
                await bot.send_photo(chat_id=user_id, photo=photo, caption=text)
            elif video:
                await bot.send_video(chat_id=user_id, video=video, caption=text)
            else:
                await bot.send_message(chat_id=user_id, text=text)
            
            successful += 1
            
        except Exception as e:
            logging.error(f"Foydalanuvchi {user_id} ga xabar yuborishda xatolik: {e}")
            failed += 1
            
        # Har 30 ta xabardan keyin 1 soniya kutish
        if (successful + failed) % 30 == 0:
            await asyncio.sleep(1)
    
    return successful, failed


def is_movie_code_valid(code: str) -> bool:
    """Kino kodi to'g'riligini tekshirish"""
    # Kod faqat harflar va raqamlardan iborat bo'lishi kerak
    return code.isalnum() and len(code) >= 1 and len(code) <= 10


def format_duration(seconds: int) -> str:
    """Vaqtni formatlash (sekund -> soat:minut:sekund)"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"