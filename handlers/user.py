from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart

from database import Database
from config import WELCOME_TEXT, SUBSCRIBED_TEXT, NOT_SUBSCRIBED_TEXT, MOVIE_NOT_FOUND_TEXT
from utils.keyboard import get_subscription_keyboard
from utils.helpers import check_user_subscription, is_movie_code_valid

user_router = Router()


@user_router.message(CommandStart())
async def start_command(message: Message, db: Database):
    """Start komandasi handleri"""
    # Foydalanuvchini bazaga qo'shish
    await db.add_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    
    # Faollikni yangilash
    await db.update_user_activity(message.from_user.id)
    
    # Majburiy obuna kanallarini olish
    channels = await db.get_all_channels()
    
    if not channels:
        # Agar kanallar yo'q bo'lsa, to'g'ridan-to'g'ri kino kodini so'rash
        await message.answer(
            f"🎬 Assalomu alaykum, {message.from_user.first_name}!\n\n"
            "Kino kodini yuboring (masalan: 001)"
        )
    else:
        # Obunani tekshirish
        is_subscribed = await check_user_subscription(message.bot, message.from_user.id, channels)
        
        if is_subscribed:
            await message.answer(SUBSCRIBED_TEXT)
        else:
            username = message.from_user.first_name or "Foydalanuvchi"
            welcome_message = WELCOME_TEXT.format(username=username)
            
            await message.answer(
                welcome_message,
                reply_markup=get_subscription_keyboard(channels)
            )


@user_router.callback_query(F.data == "check_subscription")
async def check_subscription_callback(callback: CallbackQuery, db: Database):
    """Obunani tekshirish callback handleri"""
    # Majburiy obuna kanallarini olish
    channels = await db.get_all_channels()
    
    if not channels:
        await callback.message.edit_text(SUBSCRIBED_TEXT)
        await callback.answer()
        return
    
    # Obunani tekshirish
    is_subscribed = await check_user_subscription(callback.bot, callback.from_user.id, channels)
    
    if is_subscribed:
        await callback.message.edit_text(SUBSCRIBED_TEXT)
        await callback.answer("✅ Obuna tasdiqlandi!", show_alert=True)
        
        # Faollikni yangilash
        await db.update_user_activity(callback.from_user.id)
    else:
        await callback.answer(NOT_SUBSCRIBED_TEXT, show_alert=True)


@user_router.message()
async def handle_movie_request(message: Message, db: Database):
    """Kino kodi bilan ishlash handleri"""
    # Agar xabar kino kodi bo'lmasa, e'tibor bermaslik
    if not message.text or not is_movie_code_valid(message.text.strip()):
        return
    
    # Faollikni yangilash
    await db.update_user_activity(message.from_user.id)
    
    # Majburiy obuna kanallarini olish
    channels = await db.get_all_channels()
    
    # Agar kanallar mavjud bo'lsa, obunani tekshirish
    if channels:
        is_subscribed = await check_user_subscription(message.bot, message.from_user.id, channels)
        
        if not is_subscribed:
            username = message.from_user.first_name or "Foydalanuvchi"
            welcome_message = WELCOME_TEXT.format(username=username)
            
            await message.answer(
                welcome_message,
                reply_markup=get_subscription_keyboard(channels)
            )
            return
    
    # Kino kodini olish
    movie_code = message.text.strip().upper()
    
    # Kinoni bazadan qidirish
    movie = await db.get_movie_by_code(movie_code)
    
    if movie:
        try:
            # Kinoni yuborish
            await message.answer_video(
                video=movie['file_id'],
                caption=f"🎬 {movie['title']}\n🆔 Kod: {movie['code']}"
            )
            
            # Ko'rishlar sonini oshirish
            await db.increment_movie_views(movie_code, message.from_user.id)
            
        except Exception as e:
            # Agar video yuborishda xatolik bo'lsa
            await message.answer(
                f"❌ Kino yuborishda xatolik yuz berdi.\n\n"
                f"🎬 Kino: {movie['title']}\n"
                f"🆔 Kod: {movie['code']}\n\n"
                f"Iltimos, admin bilan bog'laning."
            )
    else:
        await message.answer(MOVIE_NOT_FOUND_TEXT)