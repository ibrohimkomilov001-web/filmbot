from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import Database
from config import ADMIN_IDS
from utils.keyboard import (
    get_admin_panel_keyboard, get_channels_management_keyboard, 
    get_movies_management_keyboard, get_back_keyboard, 
    get_cancel_keyboard, get_confirm_keyboard, remove_keyboard
)
from utils.helpers import format_statistics, format_movie_info, broadcast_message, send_movie_to_base_channel
import config

admin_router = Router()


class AdminStates(StatesGroup):
    waiting_for_movie_code = State()
    waiting_for_movie_title = State()
    waiting_for_movie_file = State()
    waiting_for_channel_id = State()
    waiting_for_channel_name = State()
    waiting_for_broadcast_message = State()


# Admin panel
@admin_router.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ Sizda admin huquqlari yo'q!")
        return
    
    await message.answer(
        "👑 **Admin Panel**\n\nKerakli bo'limni tanlang:",
        reply_markup=get_admin_panel_keyboard()
    )


# Statistika
@admin_router.callback_query(F.data == "admin_stats")
async def show_statistics(callback: CallbackQuery, db: Database):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    
    # Statistikalarni olish
    stats = {
        'total_users': await db.get_users_count(),
        'today_users': await db.get_today_users_count(),
        'week_users': await db.get_week_users_count(),
        'active_users': await db.get_active_users_count(),
        'total_movies': await db.get_movies_count(),
        'total_channels': await db.get_channels_count(),
        'total_broadcasts': await db.get_total_broadcasts(),
        'total_admins': len(ADMIN_IDS)
    }
    
    text = format_statistics(stats)
    
    await callback.message.edit_text(
        text,
        reply_markup=get_back_keyboard()
    )


# Kanallar boshqaruvi
@admin_router.callback_query(F.data == "admin_channels")
async def channels_management(callback: CallbackQuery, db: Database):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    
    await callback.message.edit_text(
        "📺 **Kanallar boshqaruvi**\n\nKerakli amalni tanlang:",
        reply_markup=get_channels_management_keyboard()
    )


# Kanallar ro'yxati
@admin_router.callback_query(F.data == "channels_list")
async def show_channels_list(callback: CallbackQuery, db: Database):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    
    channels = await db.get_all_channels()
    
    if not channels:
        text = "❌ Hozircha kanallar yo'q."
    else:
        text = "📺 **Majburiy obuna kanallari:**\n\n"
        for i, channel in enumerate(channels, 1):
            text += f"{i}. {channel['channel_name']}\n"
            if channel['channel_username']:
                text += f"   @{channel['channel_username']}\n"
            text += f"   ID: `{channel['channel_id']}`\n\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_back_keyboard("admin_channels")
    )


# Kanal qo'shish
@admin_router.callback_query(F.data == "add_channel")
async def add_channel_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    
    await callback.message.edit_text(
        "➕ **Kanal qo'shish**\n\n"
        "Kanal ID sini yuboring (masalan: -1001234567890):",
        reply_markup=get_back_keyboard("admin_channels")
    )
    
    await state.set_state(AdminStates.waiting_for_channel_id)


@admin_router.message(AdminStates.waiting_for_channel_id)
async def add_channel_get_id(message: Message, state: FSMContext):
    try:
        channel_id = int(message.text)
        await state.update_data(channel_id=channel_id)
        
        await message.answer(
            "📝 Kanal nomini yuboring:",
            reply_markup=get_cancel_keyboard()
        )
        
        await state.set_state(AdminStates.waiting_for_channel_name)
        
    except ValueError:
        await message.answer("❌ Noto'g'ri format. Raqam kiriting!")


@admin_router.message(AdminStates.waiting_for_channel_name)
async def add_channel_get_name(message: Message, state: FSMContext, db: Database):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer(
            "❌ Bekor qilindi.",
            reply_markup=remove_keyboard()
        )
        return
    
    data = await state.get_data()
    channel_id = data['channel_id']
    channel_name = message.text
    
    # Kanalni bazaga qo'shish
    success = await db.add_channel(channel_id, channel_name)
    
    if success:
        await message.answer(
            f"✅ Kanal muvaffaqiyatli qo'shildi!\n\n"
            f"📺 Nom: {channel_name}\n"
            f"🆔 ID: {channel_id}",
            reply_markup=remove_keyboard()
        )
    else:
        await message.answer(
            "❌ Bu kanal allaqachon mavjud!",
            reply_markup=remove_keyboard()
        )
    
    await state.clear()


# Kanal o'chirish
@admin_router.callback_query(F.data == "delete_channel")
async def delete_channel_list(callback: CallbackQuery, db: Database):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    
    channels = await db.get_all_channels()
    
    if not channels:
        await callback.answer("❌ O'chiradigan kanallar yo'q!", show_alert=True)
        return
    
    keyboard = []
    for channel in channels:
        keyboard.append([
            InlineKeyboardButton(
                text=f"🗑 {channel['channel_name']}",
                callback_data=f"delete_ch_{channel['id']}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_channels")])
    
    await callback.message.edit_text(
        "🗑 **Kanal o'chirish**\n\nO'chiradigan kanalni tanlang:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )


@admin_router.callback_query(F.data.startswith("delete_ch_"))
async def confirm_delete_channel(callback: CallbackQuery):
    channel_id = callback.data.split("_")[-1]
    
    await callback.message.edit_text(
        "⚠️ **Ogohlantirish!**\n\n"
        "Kanalni o'chirishni tasdiqlaysizmi?",
        reply_markup=get_confirm_keyboard(f"confirm_delete_ch_{channel_id}", "admin_channels")
    )


@admin_router.callback_query(F.data.startswith("confirm_delete_ch_"))
async def delete_channel_confirm(callback: CallbackQuery, db: Database):
    channel_id = int(callback.data.split("_")[-1])
    
    success = await db.delete_channel(channel_id)
    
    if success:
        await callback.message.edit_text(
            "✅ Kanal muvaffaqiyatli o'chirildi!",
            reply_markup=get_back_keyboard("admin_channels")
        )
    else:
        await callback.message.edit_text(
            "❌ Kanalni o'chirishda xatolik!",
            reply_markup=get_back_keyboard("admin_channels")
        )


# Kinolar boshqaruvi
@admin_router.callback_query(F.data == "admin_movies")
async def movies_management(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    
    await callback.message.edit_text(
        "🎬 **Kinolar boshqaruvi**\n\nKerakli amalni tanlang:",
        reply_markup=get_movies_management_keyboard()
    )


# Kino qo'shish
@admin_router.callback_query(F.data == "add_movie")
async def add_movie_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    
    await callback.message.edit_text(
        "➕ **Kino qo'shish**\n\n"
        "Kino kodini yuboring (masalan: 001):"
    )
    
    await state.set_state(AdminStates.waiting_for_movie_code)


@admin_router.message(AdminStates.waiting_for_movie_code)
async def add_movie_get_code(message: Message, state: FSMContext):
    code = message.text.strip()
    
    if not code.isalnum():
        await message.answer("❌ Kod faqat harflar va raqamlardan iborat bo'lishi kerak!")
        return
    
    await state.update_data(code=code)
    
    await message.answer(
        f"🎬 Kino kodi: `{code}`\n\n"
        "Endi kino nomini yuboring:",
        reply_markup=get_cancel_keyboard()
    )
    
    await state.set_state(AdminStates.waiting_for_movie_title)


@admin_router.message(AdminStates.waiting_for_movie_title)
async def add_movie_get_title(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer(
            "❌ Bekor qilindi.",
            reply_markup=remove_keyboard()
        )
        return
    
    title = message.text.strip()
    await state.update_data(title=title)
    
    await message.answer(
        f"🎬 Kino nomi: {title}\n\n"
        "Endi kino videosini yuboring:",
        reply_markup=get_cancel_keyboard()
    )
    
    await state.set_state(AdminStates.waiting_for_movie_file)


@admin_router.message(AdminStates.waiting_for_movie_file)
async def add_movie_get_file(message: Message, state: FSMContext, db: Database):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer(
            "❌ Bekor qilindi.",
            reply_markup=remove_keyboard()
        )
        return
    
    if not message.video:
        await message.answer("❌ Iltimos, video fayl yuboring!")
        return
    
    data = await state.get_data()
    code = data['code']
    title = data['title']
    file_id = message.video.file_id
    
    # Kinoni bazaga qo'shish
    success = await db.add_movie(code, title, file_id)
    
    if success:
        # Baza kanalga yuborish
        bot = message.bot
        base_sent = await send_movie_to_base_channel(
            bot, config.BASE_CHANNEL_ID, code, title, file_id
        )
        
        success_text = "✅ Kino muvaffaqiyatli saqlandi!"
        if base_sent:
            success_text += "\n📤 Baza kanalga yuborildi!"
        else:
            success_text += "\n⚠️ Baza kanalga yuborishda xatolik!"
        
        await message.answer(
            success_text,
            reply_markup=remove_keyboard()
        )
    else:
        await message.answer(
            "❌ Bu kod bilan kino allaqachon mavjud!",
            reply_markup=remove_keyboard()
        )
    
    await state.clear()


# Kinolar ro'yxati
@admin_router.callback_query(F.data == "movies_list")
async def show_movies_list(callback: CallbackQuery, db: Database):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    
    movies = await db.get_all_movies()
    
    if not movies:
        text = "❌ Hozircha kinolar yo'q."
    else:
        text = f"🎬 **Barcha kinolar ({len(movies)} ta):**\n\n"
        for movie in movies[:20]:  # Faqat birinchi 20 tasi
            text += format_movie_info(movie) + "\n\n"
        
        if len(movies) > 20:
            text += f"... va yana {len(movies) - 20} ta kino"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_back_keyboard("admin_movies")
    )


# Kino o'chirish
@admin_router.callback_query(F.data == "delete_movie")
async def delete_movie_list(callback: CallbackQuery, db: Database):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    
    movies = await db.get_all_movies()
    
    if not movies:
        await callback.answer("❌ O'chiradigan kinolar yo'q!", show_alert=True)
        return
    
    keyboard = []
    for movie in movies[:10]:  # Faqat birinchi 10 ta
        keyboard.append([
            InlineKeyboardButton(
                text=f"🗑 {movie['title']} ({movie['code']})",
                callback_data=f"delete_mv_{movie['id']}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_movies")])
    
    await callback.message.edit_text(
        "🗑 **Kino o'chirish**\n\nO'chiradigan kinoni tanlang:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )


@admin_router.callback_query(F.data.startswith("delete_mv_"))
async def confirm_delete_movie(callback: CallbackQuery):
    movie_id = callback.data.split("_")[-1]
    
    await callback.message.edit_text(
        "⚠️ **Ogohlantirish!**\n\n"
        "Kinoni o'chirishni tasdiqlaysizmi?",
        reply_markup=get_confirm_keyboard(f"confirm_delete_mv_{movie_id}", "admin_movies")
    )


@admin_router.callback_query(F.data.startswith("confirm_delete_mv_"))
async def delete_movie_confirm(callback: CallbackQuery, db: Database):
    movie_id = int(callback.data.split("_")[-1])
    
    success = await db.delete_movie(movie_id)
    
    if success:
        await callback.message.edit_text(
            "✅ Kino muvaffaqiyatli o'chirildi!",
            reply_markup=get_back_keyboard("admin_movies")
        )
    else:
        await callback.message.edit_text(
            "❌ Kinoni o'chirishda xatolik!",
            reply_markup=get_back_keyboard("admin_movies")
        )


# Top kinolar
@admin_router.callback_query(F.data == "top_movies")
async def show_top_movies(callback: CallbackQuery, db: Database):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    
    movies = await db.get_top_movies(10)
    
    if not movies:
        text = "❌ Hozircha kinolar yo'q."
    else:
        text = "🏆 **Top 10 eng ko'p ko'rilgan kinolar:**\n\n"
        for i, movie in enumerate(movies, 1):
            text += f"{i}. {movie['title']}\n"
            text += f"   📊 Ko'rishlar: {movie['views']}\n"
            text += f"   🆔 Kod: `{movie['code']}`\n\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_back_keyboard("admin_movies")
    )


# Xabar yuborish
@admin_router.callback_query(F.data == "admin_broadcast")
async def broadcast_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    
    await callback.message.edit_text(
        "📢 **Ommaviy xabar yuborish**\n\n"
        "Barcha foydalanuvchilarga yuboradigan xabaringizni yozing:"
    )
    
    await state.set_state(AdminStates.waiting_for_broadcast_message)


@admin_router.message(AdminStates.waiting_for_broadcast_message)
async def broadcast_send(message: Message, state: FSMContext, db: Database):
    # Xabar ma'lumotlarini olish
    text = message.text if message.text else message.caption
    photo = message.photo[-1].file_id if message.photo else None
    video = message.video.file_id if message.video else None
    
    # Barcha foydalanuvchilar ro'yxatini olish
    user_ids = await db.get_all_users()
    total_users = len(user_ids)
    
    if total_users == 0:
        await message.answer("❌ Hozircha foydalanuvchilar yo'q!")
        await state.clear()
        return
    
    # Yuborish jarayoni haqida xabar
    progress_msg = await message.answer(
        f"📤 Xabar yuborilmoqda...\n\n"
        f"👥 Jami foydalanuvchilar: {total_users}\n"
        f"⏳ Iltimos, kuting..."
    )
    
    # Xabarni yuborish
    successful, failed = await broadcast_message(message.bot, user_ids, text, photo, video)
    
    # Statistikani saqlash
    await db.save_broadcast_stats(message.message_id, total_users, successful, failed)
    
    # Natijani ko'rsatish
    await progress_msg.edit_text(
        f"✅ **Xabar yuborish yakunlandi!**\n\n"
        f"👥 Jami foydalanuvchilar: {total_users}\n"
        f"✅ Muvaffaqiyatli: {successful}\n"
        f"❌ Xatolik: {failed}\n"
        f"📊 Muvaffaqiyat foizi: {(successful/total_users)*100:.1f}%"
    )
    
    await state.clear()


# Orqaga qaytish
@admin_router.callback_query(F.data == "admin_back")
async def admin_back(callback: CallbackQuery):
    await callback.message.edit_text(
        "👑 **Admin Panel**\n\nKerakli bo'limni tanlang:",
        reply_markup=get_admin_panel_keyboard()
    )