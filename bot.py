
import asyncio
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import F
import aiosqlite

from config import BOT_TOKEN, DATABASE_PATH, ADMIN_IDS, WELCOME_TEXT, SUBSCRIBED_TEXT, MOVIE_NOT_FOUND_TEXT, BASE_CHANNEL_ID, BASE_CHANNEL_LINK
from database import Database
from utils.keyboard import get_subscription_keyboard, get_admin_panel_keyboard, get_premium_management_keyboard, get_premium_subscription_keyboard, get_welcome_choice_keyboard, get_payment_verification_keyboard, get_card_management_keyboard, get_user_payments_keyboard, get_admin_management_keyboard, get_admin_permissions_keyboard, get_admin_actions_keyboard
from utils.helpers import check_user_subscription, is_movie_code_valid, format_statistics, send_movie_to_base_channel


# Logging sozlash
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global database
db = None

# FSM States - Kino qo'shish uchun
class MovieStates(StatesGroup):
    waiting_for_code = State()
    waiting_for_title = State()
    waiting_for_video = State()
    waiting_for_4k_movie_code = State()
    waiting_for_4k_video = State()

# FSM States - Kanal qo'shish uchun
# ...existing code...

async def main():
    global db
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    db = Database(DATABASE_PATH)
    await db.init_database()
    await db.init_premium_settings()

    # Admin boshqaruvi tugmasi handleri
    @dp.callback_query(F.data == "admin_management")
    async def admin_management_handler(callback: CallbackQuery):
        if callback.from_user.id not in ADMIN_IDS:
            await callback.answer("❌ Sizda admin huquqlari yo'q!", show_alert=True)
            return

        text = (
            "👑 *Admin Boshqaruvi*\n\n"
            "🔧 *Bot adminlari boshqaruvi:*\n"
            "• Admin qo'shish va o'chirish\n"
            "• Huquqlarni boshqarish\n"
            "• Adminlar ro'yxatini ko'rish\n\n"
            "⚠️ *Diqqat: Faqat super admin adminlarni boshqara oladi!*"
        )
        await callback.message.edit_text(
            text,
            reply_markup=get_admin_management_keyboard(),
            parse_mode="Markdown"
        )

    # Huquqlar tugmasi handleri
    @dp.callback_query(F.data == "admin_permissions")
    async def admin_permissions_handler(callback: CallbackQuery):
        if callback.from_user.id not in ADMIN_IDS:
            await callback.answer("❌ Sizda admin huquqlari yo'q!", show_alert=True)
            return


            # Admin qo'shish komandasi: /add_admin <user_id>
            @dp.message(Command("add_admin"))
            async def add_admin_command(message: Message):
                # Faqat adminlar ishlata oladi
                if message.from_user.id not in ADMIN_IDS:
                    await message.answer("❌ Sizda admin huquqlari yo'q!")
                    return

                # Komanda: /add_admin <user_id>
                args = message.text.split()
                if len(args) != 2 or not args[1].isdigit():
                    await message.answer("❌ Foydalanish: /add_admin <user_id>")
                    return

                new_admin_id = int(args[1])
                if new_admin_id in ADMIN_IDS:
                    await message.answer("ℹ️ Bu foydalanuvchi allaqachon admin.")
                    return

                # Bazaga admin qo'shish (agar kerak bo'lsa)
                try:
                    # ADMIN_IDS ni yangilash uchun config.py yoki DB ishlatiladi
                    # Agar ADMIN_IDS faqat config.py da bo'lsa, faqat DB ga qo'shish mumkin
                    await db.add_admin(new_admin_id)
                    ADMIN_IDS.append(new_admin_id)
                    await message.answer(f"✅ Yangi admin muvaffaqiyatli qo'shildi!\n🆔 User ID: <code>{new_admin_id}</code>", parse_mode="HTML")
                except Exception as e:
                    await message.answer(f"❌ Admin qo'shishda xatolik: {e}")
        text = (
            "⚙️ *Admin Huquqlari Boshqaruvi*\n\n"
            "Quyidagi huquqlardan birini tanlang yoki admin huquqlarini o'zgartiring.\n\n"
            "🔰 Asosiy - Botni boshqarish\n"
            "📊 Statistika - Foydalanuvchi va kino statistikasi\n"
            "🎬 Kinolar - Kino qo'shish/o'chirish\n"
            "📺 Kanallar - Kanal boshqaruvi\n"
            "📢 Xabar yuborish - Ommaviy xabar\n"
            "💎 Premium - Premium boshqaruvi\n"
        )
        await callback.message.edit_text(
            text,
            reply_markup=get_admin_permissions_keyboard(),
            parse_mode="Markdown"
        )

# ...existing code...
import asyncio
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import F

from config import BOT_TOKEN, DATABASE_PATH, ADMIN_IDS, WELCOME_TEXT, SUBSCRIBED_TEXT, MOVIE_NOT_FOUND_TEXT, BASE_CHANNEL_ID, BASE_CHANNEL_LINK
from database import Database
from utils.keyboard import get_subscription_keyboard, get_admin_panel_keyboard, get_premium_management_keyboard, get_premium_subscription_keyboard, get_welcome_choice_keyboard, get_payment_verification_keyboard, get_card_management_keyboard, get_user_payments_keyboard, get_admin_management_keyboard, get_admin_permissions_keyboard, get_admin_actions_keyboard
from utils.helpers import check_user_subscription, is_movie_code_valid, format_statistics, send_movie_to_base_channel


# Logging sozlash
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global database
db = None

# FSM States - Kino qo'shish uchun
class MovieStates(StatesGroup):
    waiting_for_code = State()
    waiting_for_title = State()
    waiting_for_video = State()
    waiting_for_4k_movie_code = State()
    waiting_for_4k_video = State()

# FSM States - Kanal qo'shish uchun
class ChannelStates(StatesGroup):
    waiting_for_channel_name = State()
    waiting_for_channel_username = State()
    waiting_for_channel_forward = State()

# FSM States - Broadcast uchun  
class BroadcastStates(StatesGroup):
    waiting_for_message = State()
    waiting_for_confirmation = State()

# FSM States - Premium obuna uchun
class PremiumStates(StatesGroup):
    waiting_for_price_1oy = State()
    waiting_for_price_3oy = State()
    waiting_for_price_6oy = State()
    waiting_for_price_12oy = State()
    waiting_for_description = State()

# FSM States - To'lov kartalari uchun
class CardStates(StatesGroup):
    waiting_for_card_number = State()
    waiting_for_card_holder_name = State()

# FSM States - To'lov uchun
class PaymentStates(StatesGroup):
    waiting_for_receipt = State()


class AdminStates(StatesGroup):
    waiting_for_admin_id = State()
    waiting_for_remove_admin_id = State()
    waiting_for_permission_admin_id = State()


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
    await db.init_premium_settings()

    # ADMIN_IDS dagi adminlarni bazaga avtomatik qo'shish
    from config import ADMIN_IDS
    for admin_id in ADMIN_IDS:
        # Foydalanuvchi ma'lumotlarini olish (agar bor bo'lsa)
        user = await db.get_user(admin_id)
        username = user['username'] if user and user.get('username') else None
        first_name = user['first_name'] if user and user.get('first_name') else None
        # Bazaga admin sifatida qo'shish (agar yo'q bo'lsa yoki faol bo'lmasa)
        if db.db_path:
            async with aiosqlite.connect(db.db_path) as adb:
                await adb.execute('''
                    INSERT OR IGNORE INTO bot_admins (user_id, username, first_name, permissions, is_active)
                    VALUES (?, ?, ?, ?, TRUE)
                ''', (admin_id, username, first_name, 'super'))
                await adb.execute('''
                    UPDATE bot_admins SET is_active=TRUE WHERE user_id=?
                ''', (admin_id,))
                await adb.commit()
    
    # Start komandasi
    @dp.message(CommandStart())
    async def start_command(message: Message):
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
        
        # Premium obunasini tekshirish
        has_premium = await db.check_user_premium(message.from_user.id)
        premium_settings = await db.get_premium_settings()
        
        # Agar Premium obunasi bo'lsa, to'g'ridan-to'g'ri kino so'rash
        if has_premium:
            username = message.from_user.first_name or "Foydalanuvchi"
            await message.answer(
                f"💎 **Premium foydalanuvchi!**\n\n"
                f"🎬 Salom, {username}! Premium obunangiz faol.\n\n"
                f"🔍 **Kino kodini yuboring:**\n"
                f"Masalan: `ABC123`"
            )
            return
        
        username = message.from_user.first_name or "Foydalanuvchi"
        
        # Tanlov menyusini ko'rsatish
        welcome_text = f"🎬 **Salom, {username}!**\n\n"
        welcome_text += f"🤖 **Botimizga xush kelibsiz!**\n\n"
        
        if premium_settings['is_enabled']:
            welcome_text += f"📋 **Obuna turlari:**\n\n"
            welcome_text += f"💎 **Premium obuna:**\n"
            welcome_text += f"• ✅ Majburiy obuna yo'q\n"
            welcome_text += f"• ⚡ Tez kino olish\n"
            welcome_text += f"• 🎯 To'g'ridan-to'g'ri kirish\n"
            welcome_text += f"• 🎬 4K formatda tomosha\n"
            welcome_text += f"• 💰 Narx: {premium_settings['price_1month']:,} so'm/oy\n\n"
            welcome_text += f"🆓 **Bepul ko'rish:**\n"
            welcome_text += f"• 📢 Majburiy obuna talab\n"
            welcome_text += f"• 🔒 Kanallaraga obuna bo'lish\n"
            welcome_text += f"• 💸 Pulsiz foydalanish\n\n"
            welcome_text += f"👇 **Birini tanlang:**"
            
            await message.answer(
                welcome_text,
                reply_markup=get_welcome_choice_keyboard()
            )
        else:
            # Premium o'chirilgan bo'lsa, faqat bepul
            channels = await db.get_all_channels()
            is_subscribed = await check_user_subscription(bot, message.from_user.id, channels, db)
            
            if is_subscribed:
                await message.answer(
                    f"🎬 Salom, {username}!\n\n"
                    f"🔍 **Kino kodini yuboring:**\n"
                    f"Masalan: `ABC123`"
                )
            else:
                welcome_message = WELCOME_TEXT.format(username=username)
                await message.answer(
                    welcome_message,
                    reply_markup=get_subscription_keyboard(channels, False)
                )

    # Premium tanlash
    @dp.callback_query(F.data == "choose_premium")
    async def choose_premium_option(callback: CallbackQuery):
        premium_settings = await db.get_premium_settings()
        
        if not premium_settings['is_enabled']:
            await callback.answer("❌ Premium obuna hozircha mavjud emas!", show_alert=True)
            return
        
        # Foydalanuvchi premium obunasini tekshirish
        has_premium = await db.check_user_premium(callback.from_user.id)
        
        if has_premium:
            await callback.answer("✅ Sizda allaqachon Premium obuna mavjud!", show_alert=True)
            username = callback.from_user.first_name or "Foydalanuvchi"
            await callback.message.edit_text(
                f"💎 **Premium foydalanuvchi!**\n\n"
                f"🎬 Salom, {username}! Premium obunangiz faol.\n\n"
                f"🔍 **Kino kodini yuboring:**\n"
                f"Masalan: `ABC123`"
            )
            return
        
        text = f"💎 **Premium Obuna**\n\n"
        text += f"🌟 **Afzalliklari:**\n"
        text += f"• ✅ Majburiy obuna yo'q\n"
        text += f"• ⚡ Tezkor kino yuklab olish\n"
        text += f"• 🎯 To'g'ridan-to'g'ri kirish\n"
        text += f"• 🎬 4K formatda tomosha\n"
        text += f"• 🚫 Reklama yo'q\n\n"
        text += f"💰 **Narxlar:**\n"
        text += f"• 1 oy: {premium_settings['price_1month']:,} so'm\n"
        text += f"• 3 oy: {premium_settings['price_3months']:,} so'm\n"
        text += f"• 6 oy: {premium_settings['price_6months']:,} so'm\n"
        text += f"• 12 oy: {premium_settings['price_12months']:,} so'm\n\n"
        text += f"💳 **To'lov:** Admin bilan bog'laning"
        
        await callback.message.edit_text(
            text,
            reply_markup=get_premium_subscription_keyboard(premium_settings)
        )

    # Bepul tanlash
    @dp.callback_query(F.data == "choose_free")
    async def choose_free_option(callback: CallbackQuery):
        channels = await db.get_all_channels()
        
        if not channels:
            username = callback.from_user.first_name or "Foydalanuvchi"
            await callback.message.edit_text(
                f"🆓 **Bepul foydalanish**\n\n"
                f"🎬 Salom, {username}!\n\n"
                f"🔍 **Kino kodini yuboring:**\n"
                f"Masalan: `ABC123`"
            )
            return
        
        # Obunani tekshirish
        is_subscribed = await check_user_subscription(bot, callback.from_user.id, channels, db)
        
        if is_subscribed:
            username = callback.from_user.first_name or "Foydalanuvchi"
            await callback.message.edit_text(
                f"🆓 **Bepul foydalanish**\n\n"
                f"🎬 Salom, {username}!\n\n"
                f"🔍 **Kino kodini yuboring:**\n"
                f"Masalan: `ABC123`"
            )
        else:
            username = callback.from_user.first_name or "Foydalanuvchi"
            
            text = f"🆓 **Bepul ko'rish**\n\n"
            text += f"📢 **Majburiy obuna:**\n"
            text += f"Kinolarni ko'rish uchun quyidagi kanallarga obuna bo'ling:\n\n"
            
            await callback.message.edit_text(
                text,
                reply_markup=get_subscription_keyboard(channels, False)
            )

    # Foydalanuvchi to'lovlarini ko'rish
    @dp.callback_query(F.data == "my_payments")
    async def show_my_payments(callback: CallbackQuery):
        # Foydalanuvchi premium holatini tekshirish
        premium_info = await db.check_premium_expiry(callback.from_user.id)
        
        # Faqat tasdiqlangan to'lovlarni olish
        completed_payments = await db.get_user_completed_payments(callback.from_user.id)
        
        text = "💳 **Mening to'lovlarim**\n\n"
        
        # Premium holati
        if premium_info['has_premium']:
            remaining = premium_info['remaining_days']
            end_date = premium_info['end_date'].strftime("%d.%m.%Y")
            subscription_type = premium_info['subscription_type']
            
            if premium_info['is_expiring_soon']:
                text += "⚠️ **Premium obuna tugash arafasida!**\n\n"
            else:
                text += "✅ **Premium obuna faol**\n\n"
            
            text += f"📅 **Tugash sanasi:** {end_date}\n"
            text += f"⏰ **Qolgan kunlar:** {remaining} kun\n"
            text += f"📦 **Obuna turi:** {subscription_type}\n\n"
            
            if remaining <= 3:
                text += "🔄 **Obunani yangilamoqchimisiz?**\n\n"
        else:
            text += "❌ **Premium obuna yo'q**\n\n"
        
        # Tasdiqlangan to'lovlar tarixini ko'rsatish
        if completed_payments:
            text += f"📋 **Tasdiqlangan to'lovlar ({len(completed_payments)} ta)**\n\n"
            for i, payment in enumerate(completed_payments[:5], 1):  # Oxirgi 5 ta to'lov
                amount = f"{payment['amount']:,}"
                subscription = payment['subscription_type']
                payment_date = payment['payment_date'].split()[0]  # Faqat sana
                text += f"{i}. 💰 {amount} so'm - {subscription}\n"
                text += f"   📅 {payment_date}\n\n"
            
            if len(completed_payments) > 5:
                text += f"... va yana {len(completed_payments) - 5} ta to'lov\n\n"
        else:
            text += "📝 **To'lovlar tarixingiz bo'sh**\n\n"
            text += "💎 Premium obuna uchun to'lov qiling."
        
        await callback.message.edit_text(
            text,
            reply_markup=get_user_payments_keyboard()
        )

    # Foydalanuvchi menuga qaytish
    @dp.callback_query(F.data == "user_back_to_menu")
    async def user_back_to_menu(callback: CallbackQuery):
        premium_settings = await db.get_premium_settings()
        username = callback.from_user.first_name or "Foydalanuvchi"
        
        # Tanlov menyusini ko'rsatish
        welcome_text = f"🎬 **Salom, {username}!**\n\n"
        welcome_text += f"🤖 **Botimizga xush kelibsiz!**\n\n"
        
        if premium_settings['is_enabled']:
            welcome_text += f"📋 **Obuna turlari:**\n\n"
            welcome_text += f"💎 **Premium** - Majburiy obuna yo'q\n"
            welcome_text += f"🆓 **Bepul** - Kanallarga obuna bo'ling\n\n"
        else:
            welcome_text += f"🔍 **Kino kodini yuboring:**\n"
            welcome_text += f"Masalan: `ABC123`\n\n"
        
        welcome_text += f"👇 **Tanlang:**"
        
        await callback.message.edit_text(
            welcome_text,
            reply_markup=get_welcome_choice_keyboard()
        )

    # Admin panel
    @dp.message(Command("admin"))
    async def admin_panel(message: Message):
        if message.from_user.id not in ADMIN_IDS:
            await message.answer("❌ Sizda admin huquqlari yo'q!")
            return
        
        await message.answer(
            "👑 **Admin Panel**\n\nKerakli bo'limni tanlang:",
            reply_markup=get_admin_panel_keyboard()
        )

    # Admin panel tugmalari
    @dp.callback_query(F.data == "admin_stats")
    async def show_admin_stats(callback: CallbackQuery):
        if callback.from_user.id not in ADMIN_IDS:
            await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
            return
        
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
        
        from utils.keyboard import get_back_keyboard
        await callback.message.edit_text(
            text,
            reply_markup=get_back_keyboard()
        )

    @dp.callback_query(F.data == "admin_channels")
    async def show_admin_channels(callback: CallbackQuery):
        if callback.from_user.id not in ADMIN_IDS:
            await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
            return
        
        from utils.keyboard import get_channels_management_keyboard
        await callback.message.edit_text(
            "📺 **Kanallar boshqaruvi**\n\nKerakli amalni tanlang:",
            reply_markup=get_channels_management_keyboard()
        )

    @dp.callback_query(F.data == "admin_movies")
    async def show_admin_movies(callback: CallbackQuery):
        if callback.from_user.id not in ADMIN_IDS:
            await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
            return
        
        from utils.keyboard import get_movies_management_keyboard
        await callback.message.edit_text(
            "🎬 **Kinolar boshqaruvi**\n\nKerakli amalni tanlang:",
            reply_markup=get_movies_management_keyboard()
        )

    # Kino qo'shish - boshlash
    @dp.callback_query(F.data == "add_movie")
    async def add_movie_start(callback: CallbackQuery, state: FSMContext):
        if callback.from_user.id not in ADMIN_IDS:
            await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
            return
        
        await callback.message.edit_text(
            "➕ **Kino qo'shish**\n\n"
            "Kino kodini yuboring ? :"
        )
        
        await state.set_state(MovieStates.waiting_for_code)

    # Kino kodi qabul qilish
    @dp.message(MovieStates.waiting_for_code)
    async def add_movie_get_code(message: Message, state: FSMContext):
        if message.from_user.id not in ADMIN_IDS:
            return
            
        code = message.text.strip().upper()
        
        if not code.isalnum():
            await message.answer("❌ Kod faqat harflar va raqamlardan iborat bo'lishi kerak!\nQaytadan kiriting:")
            return
        
        # Kod mavjudligini tekshirish
        existing_movie = await db.get_movie_by_code(code)
        if existing_movie:
            await message.answer(f"❌ Bu kod ({code}) allaqachon mavjud!\nBoshqa kod kiriting:")
            return
        
        await state.update_data(code=code)
        
        await message.answer(
            f"✅ Kino kodi: `{code}`\n\n"
            "Endi kino nomini yuboring ☺️ :"
        )
        
        await state.set_state(MovieStates.waiting_for_title)

    # Kino nomi qabul qilish
    @dp.message(MovieStates.waiting_for_title)
    async def add_movie_get_title(message: Message, state: FSMContext):
        if message.from_user.id not in ADMIN_IDS:
            return
            
        if not message.text:
            await message.answer("❌ Iltimos, kino nomini matn ko'rinishida yuboring!")
            return
            
        title = message.text.strip()
        await state.update_data(title=title)
        
        await message.answer(
            f"✅ Kino nomi: {title}\n\n"
            "Endi kino videosini yuboring:"
        )
        
        await state.set_state(MovieStates.waiting_for_video)

    # Video fayl qabul qilish
    @dp.message(MovieStates.waiting_for_video)
    async def add_movie_get_video(message: Message, state: FSMContext):
        if message.from_user.id not in ADMIN_IDS:
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
            success_text = "✅ **Kino muvaffaqiyatli saqlandi!**\n\n"

            success_text += f"🎬 Nomi: {title}\n"

            success_text += f"🆔 Kodi: {code}\n\n"
            
            # Baza kanalga yuborish (agar ID mavjud bo'lsa)
            if BASE_CHANNEL_ID:
                base_sent, base_message = await send_movie_to_base_channel(
                    bot, BASE_CHANNEL_ID, code, title, file_id
                )
                
                if base_sent:
                    success_text += f"📤 **Baza kanalga yuborildi!**\n"
                    success_text += f"🔗 Kanal: {BASE_CHANNEL_LINK}\n"
                    success_text += f"ℹ️ {base_message}"
                else:
                    success_text += f"⚠️ **Baza kanalga yuborishda xatolik!**\n"
                    success_text += f"❌ Sabab: {base_message}\n\n"
                    success_text += f"**Hal qilish:**\n"
                    success_text += f"1. Admin bilan bog'laning\n"
                    success_text += f"2. Kanal ID ni to'g'rilang\n"
                    success_text += f"3. Botni kanalga admin qiling"
            else:
                success_text += f"ℹ️ **Baza kanal sozlanmagan**\n"
                success_text += f"📝 Admin config.py da BASE_CHANNEL_ID ni o'rnatishi kerak\n\n"
                success_text += f"**Kanal ID topish:**\n"
                success_text += f"1. Botni kanalga qo'shing\n"
                success_text += f"2. @userinfobot dan kanal ID ni oling\n"
                success_text += f"3. config.py da BASE_CHANNEL_ID = -1001234567890"
            
            await message.answer(success_text)
        else:
            await message.answer(
                "❌ Bu kod bilan kino allaqachon mavjud!"
            )
        
        await state.clear()

    # 4K qo'shish
    @dp.callback_query(F.data == "add_4k")
    async def add_4k_start(callback: CallbackQuery, state: FSMContext):
        if callback.from_user.id not in ADMIN_IDS:
            await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
            return
        
        await callback.message.edit_text(
            "🎬 **4K Video Qo'shish**\n\n"
            "📝 **Mavjud kinoga 4K formatda video qo'shing**\n\n"
            "🆔 **Kino kodini kiriting:**\n"
            "Masalan: `ABC123`\n\n"
            "❌ **Bekor qilish:** /cancel"
        )
        
        await state.set_state(MovieStates.waiting_for_4k_movie_code)

    @dp.message(MovieStates.waiting_for_4k_movie_code)
    async def get_4k_movie_code(message: Message, state: FSMContext):
        if message.from_user.id not in ADMIN_IDS:
            return
            
        if message.text and message.text.lower() in ['/cancel', 'cancel', 'bekor']:
            await message.answer(
                "❌ **4K qo'shish bekor qilindi**",
                reply_markup=get_admin_panel_keyboard()
            )
            await state.clear()
            return
        
        if not message.text:
            await message.answer("❌ Iltimos, kino kodini matn shaklida yuboring!")
            return
            
        movie_code = message.text.strip().upper()
        
        # Kino mavjudligini tekshirish
        movie = await db.get_movie_by_code(movie_code)
        
        if not movie:
            await message.answer(f"❌ **Kino topilmadi!**\n\nKod: `{movie_code}`\n\nIltimos, to'g'ri kino kodini kiriting.")
            return
        
        # Ma'lumotlarni saqlash
        await state.update_data(movie_id=movie['id'], movie_code=movie_code, movie_title=movie['title'])
        
        # 4K mavjudligini tekshirish
        if movie.get('file_id_4k'):
            await message.answer(
                f"⚠️ **Bu kinoda allaqachon 4K mavjud!**\n\n"
                f"🎬 **Kino:** {movie['title']}\n"
                f"🆔 **Kod:** {movie_code}\n\n"
                f"❓ **Yangi 4K video bilan almashtirmoqchimisiz?**\n\n"
                f"📹 **Yangi 4K videoni yuboring yoki bekor qiling:**"
            )
        else:
            await message.answer(
                f"✅ **Kino topildi!**\n\n"
                f"🎬 **Kino:** {movie['title']}\n" 
                f"🆔 **Kod:** {movie_code}\n\n"
                f"📹 **Endi 4K videoni yuboring:**"
            )
        
        await state.set_state(MovieStates.waiting_for_4k_video)

    @dp.message(MovieStates.waiting_for_4k_video)
    async def get_4k_video(message: Message, state: FSMContext):
        if message.from_user.id not in ADMIN_IDS:
            return
            
        if message.text and message.text.lower() in ['/cancel', 'cancel', 'bekor']:
            await message.answer(
                "❌ **4K qo'shish bekor qilindi**",
                reply_markup=get_admin_panel_keyboard()
            )
            await state.clear()
            return
        
        if not message.video:
            await message.answer("❌ Iltimos, video fayl yuboring!")
            return
            
        data = await state.get_data()
        movie_id = data['movie_id']
        movie_code = data['movie_code']
        movie_title = data['movie_title']
        
        # 4K videoni bazaga saqlash
        success = await db.update_movie_4k(movie_id, message.video.file_id)
        
        if success:
            await message.answer(
                f"✅ **4K video muvaffaqiyatli qo'shildi!**\n\n"
                f"🎬 **Kino:** {movie_title}\n"
                f"🆔 **Kod:** {movie_code}\n"
                f"📹 **4K Video ID:** `{message.video.file_id}`\n\n"
                f"💎 **Premium foydalanuvchilar endi bu kinoni 4K formatda ko'ra oladi!**"
            )
        else:
            await message.answer(f"❌ **4K video qo'shishda xatolik!**\n\nIltimos, qayta urinib ko'ring.")
        
        await state.clear()

    @dp.callback_query(F.data == "admin_broadcast")
    async def show_admin_broadcast(callback: CallbackQuery, state: FSMContext):
        if callback.from_user.id not in ADMIN_IDS:
            await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
            return
        
        # Foydalanuvchilar sonini olish
        total_users = await db.get_users_count()
        
        await callback.message.edit_text(
            f"📢 **Ommaviy xabar yuborish**\n\n"
            f"👥 **Jami foydalanuvchilar:** {total_users} ta\n\n"
            f"📝 **Yubormoqchi bo'lgan xabaringizni yozing:**\n\n"
            f"📋 **Qo'llab-quvvatlanadigan formatlar:**\n"
            f"• 📄 Matn xabarlari\n"
            f"• 🖼 Rasm + matn\n"
            f"• 🎥 Video + matn\n"
            f"• 📎 Hujjat + matn\n\n"
            f"❌ **Bekor qilish:** /cancel"
        )
        
        await state.set_state(BroadcastStates.waiting_for_message)

    # Broadcast xabarni qabul qilish
    @dp.message(BroadcastStates.waiting_for_message)
    async def receive_broadcast_message(message: Message, state: FSMContext):
        if message.from_user.id not in ADMIN_IDS:
            return
            
        # Cancel buyrug'ini tekshirish
        if message.text and message.text.lower() in ['/cancel', 'cancel', 'bekor']:
            await message.answer(
                "❌ **Ommaviy xabar yuborish bekor qilindi**",
                reply_markup=get_admin_panel_keyboard()
            )
            await state.clear()
            return
        
        # Xabar turini aniqlash va saqlash
        message_data = {}
        
        if message.text:
            message_data = {
                'type': 'text',
                'text': message.text
            }
            preview_text = f"📄 **Matn xabar:**\n\n{message.text}"
            
        elif message.photo:
            message_data = {
                'type': 'photo',
                'photo': message.photo[-1].file_id,
                'caption': message.caption or ''
            }
            preview_text = f"🖼 **Rasm xabar:**\n\n{message.caption or 'Rasm (matn yoq)'}"
            
        elif message.video:
            message_data = {
                'type': 'video', 
                'video': message.video.file_id,
                'caption': message.caption or ''
            }
            preview_text = f"🎥 **Video xabar:**\n\n{message.caption or 'Video (matn yoq)'}"
            
        elif message.document:
            message_data = {
                'type': 'document',
                'document': message.document.file_id,
                'caption': message.caption or ''
            }
            preview_text = f"📎 **Hujjat xabar:**\n\n{message.caption or 'Hujjat (matn yoq)'}"
            
        else:
            await message.answer("❌ **Qo'llab-quvvatlanmagan xabar turi!**\n\nIltimos, matn, rasm, video yoki hujjat yuboring.")
            return
        
        # Ma'lumotlarni saqlash
        await state.update_data(broadcast_data=message_data)
        
        # Foydalanuvchilar sonini olish
        total_users = await db.get_users_count()
        
        # Tasdiqlash xabari
        confirm_text = f"✅ **Xabar qabul qilindi!**\n\n"
        confirm_text += f"👥 **Yuboriluvchilar:** {total_users} ta foydalanuvchi\n\n"
        confirm_text += f"📋 **Xabar ko'rinishi:**\n"
        confirm_text += f"{'='*30}\n"
        confirm_text += f"{preview_text}\n"
        confirm_text += f"{'='*30}\n\n"
        confirm_text += f"❓ **Ushbu xabarni barcha foydalanuvchilarga yuborishni tasdiqlaysizmi?**"
        
        # Tasdiqlash tugmalari
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Ha, yuborish", callback_data="broadcast_confirm"),
                InlineKeyboardButton(text="❌ Bekor qilish", callback_data="broadcast_cancel")
            ]
        ])
        
        await message.answer(confirm_text, reply_markup=keyboard)
        await state.set_state(BroadcastStates.waiting_for_confirmation)

    # Broadcast tasdiqlash
    @dp.callback_query(F.data == "broadcast_confirm")
    async def confirm_broadcast(callback: CallbackQuery, state: FSMContext):
        if callback.from_user.id not in ADMIN_IDS:
            await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
            return
            
        # Xabar ma'lumotlarini olish
        data = await state.get_data()
        broadcast_data = data.get('broadcast_data', {})
        
        if not broadcast_data:
            await callback.answer("❌ Xabar ma'lumotlari topilmadi!", show_alert=True)
            return
        
        # Yuborish jarayonini boshlash
        await callback.message.edit_text("🚀 **Ommaviy xabar yuborish boshlandi...**\n\n⏳ Iltimos, kuting...")
        
        # Barcha foydalanuvchilarni olish
        users = await db.get_all_users()
        
        success_count = 0
        failed_count = 0
        
        # Har bir foydalanuvchiga xabar yuborish
        for user in users:
            try:
                user_id = user[0]  # user_id birinchi ustun
                
                if broadcast_data['type'] == 'text':
                    await bot.send_message(user_id, broadcast_data['text'])
                    
                elif broadcast_data['type'] == 'photo':
                    await bot.send_photo(
                        user_id, 
                        broadcast_data['photo'],
                        caption=broadcast_data['caption']
                    )
                    
                elif broadcast_data['type'] == 'video':
                    await bot.send_video(
                        user_id,
                        broadcast_data['video'], 
                        caption=broadcast_data['caption']
                    )
                    
                elif broadcast_data['type'] == 'document':
                    await bot.send_document(
                        user_id,
                        broadcast_data['document'],
                        caption=broadcast_data['caption']
                    )
                
                success_count += 1
                
                # Har 10 ta xabardan keyin biroz pauza
                if success_count % 10 == 0:
                    await asyncio.sleep(0.5)
                    
            except Exception as e:
                failed_count += 1
                print(f"Xabar yuborishda xatolik (user_id: {user_id}): {e}")
                continue
        
        # Natijani ko'rsatish
        result_text = f"✅ **Ommaviy xabar yuborish yakunlandi!**\n\n"
        result_text += f"📊 **Natijalar:**\n"
        result_text += f"• ✅ Muvaffaqiyatli: {success_count} ta\n"
        result_text += f"• ❌ Xatolik: {failed_count} ta\n"
        result_text += f"• 📈 Muvaffaqiyat foizi: {(success_count/(success_count+failed_count)*100):.1f}%\n\n"
        result_text += f"📅 **Sana:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Statistikaga qo'shish
        await db.save_broadcast_stats(0, success_count + failed_count, success_count, failed_count)
        
        await callback.message.edit_text(result_text, reply_markup=get_admin_panel_keyboard())
        await state.clear()

    # Broadcast bekor qilish
    @dp.callback_query(F.data == "broadcast_cancel")
    async def cancel_broadcast(callback: CallbackQuery, state: FSMContext):
        if callback.from_user.id not in ADMIN_IDS:
            await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
            return
            
        await callback.message.edit_text(
            "❌ **Ommaviy xabar yuborish bekor qilindi**",
            reply_markup=get_admin_panel_keyboard()
        )
        await state.clear()

    # Premium obuna boshqaruvi
    @dp.callback_query(F.data == "admin_premium")
    async def show_premium_management(callback: CallbackQuery):
        if callback.from_user.id not in ADMIN_IDS:
            await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
            return
        
        premium_settings = await db.get_premium_settings()
        premium_users_count = await db.get_premium_users_count()
        
        text = f"💎 **Premium Obuna Boshqaruvi**\n\n"
        text += f"📊 **Holat:** {'🟢 Faol' if premium_settings['is_enabled'] else '🔴 Faol emas'}\n"
        text += f"👥 **Premium foydalanuvchilar:** {premium_users_count} ta\n\n"
        text += f"💰 **Narxlar:**\n"
        text += f"• 1 oy: {premium_settings['price_1month']:,} so'm\n"
        text += f"• 3 oy: {premium_settings['price_3months']:,} so'm\n"
        text += f"• 6 oy: {premium_settings['price_6months']:,} so'm\n"
        text += f"• 12 oy: {premium_settings['price_12months']:,} so'm\n\n"
        text += f"📝 **Tavsif:** {premium_settings['description']}"
        
        await callback.message.edit_text(
            text,
            reply_markup=get_premium_management_keyboard(premium_settings['is_enabled'])
        )

    # Premium narxlarni sozlash
    @dp.callback_query(F.data == "premium_prices")
    async def edit_premium_prices(callback: CallbackQuery, state: FSMContext):
        if callback.from_user.id not in ADMIN_IDS:
            await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
            return
        
        await callback.message.edit_text(
            "💰 **Premium narxlarni sozlash**\n\n"
            "1️⃣ **1 oylik obuna narxini kiriting:**\n"
            "Masalan: 5000\n\n"
            "❌ **Bekor qilish:** /cancel"
        )
        
        await state.set_state(PremiumStates.waiting_for_price_1oy)

    @dp.message(PremiumStates.waiting_for_price_1oy)
    async def get_price_1m(message: Message, state: FSMContext):
        if message.from_user.id not in ADMIN_IDS:
            return
            
        if message.text and message.text.lower() in ['/cancel', 'cancel']:
            await message.answer("❌ **Narx sozlash bekor qilindi**")
            await state.clear()
            return
        
        try:
            price_1m = int(message.text)
            if price_1m < 1000:
                await message.answer("❌ Narx kamida 1000 so'm bo'lishi kerak!")
                return
                
            await state.update_data(price_1m=price_1m)
            
            await message.answer(
                f"✅ 1 oylik: {price_1m:,} so'm\n\n"
                "2️⃣ **3 oylik obuna narxini kiriting:**"
            )
            
            await state.set_state(PremiumStates.waiting_for_price_3oy)
            
        except ValueError:
            await message.answer("❌ Faqat raqam kiriting!")

    @dp.message(PremiumStates.waiting_for_price_3oy)
    async def get_price_3m(message: Message, state: FSMContext):
        if message.from_user.id not in ADMIN_IDS:
            return
            
        try:
            price_3m = int(message.text)
            if price_3m < 3000:
                await message.answer("❌ Narx kamida 3000 so'm bo'lishi kerak!")
                return
                
            await state.update_data(price_3m=price_3m)
            
            await message.answer(
                f"✅ 3 oylik: {price_3m:,} so'm\n\n"
                "3️⃣ **6 oylik obuna narxini kiriting:**"
            )
            
            await state.set_state(PremiumStates.waiting_for_price_6oy)
            
        except ValueError:
            await message.answer("❌ Faqat raqam kiriting!")

    @dp.message(PremiumStates.waiting_for_price_6oy)
    async def get_price_6m(message: Message, state: FSMContext):
        if message.from_user.id not in ADMIN_IDS:
            return
            
        try:
            price_6m = int(message.text)
            if price_6m < 5000:
                await message.answer("❌ Narx kamida 5000 so'm bo'lishi kerak!")
                return
                
            await state.update_data(price_6m=price_6m)
            
            await message.answer(
                f"✅ 6 oylik: {price_6m:,} so'm\n\n"
                "4️⃣ **12 oylik obuna narxini kiriting:**"
            )
            
            await state.set_state(PremiumStates.waiting_for_price_12oy)
            
        except ValueError:
            await message.answer("❌ Faqat raqam kiriting!")

    @dp.message(PremiumStates.waiting_for_price_12oy)
    async def get_price_12m(message: Message, state: FSMContext):
        if message.from_user.id not in ADMIN_IDS:
            return
            
        try:
            price_12m = int(message.text)
            if price_12m < 10000:
                await message.answer("❌ Narx kamida 10000 so'm bo'lishi kerak!")
                return
                
            data = await state.get_data()
            price_1m = data['price_1m']
            price_3m = data['price_3m']
            price_6m = data['price_6m']
            
            # Narxlarni yangilash
            await db.update_premium_prices(price_1m, price_3m, price_6m, price_12m)
            
            await message.answer(
                f"✅ **Premium narxlar muvaffaqiyatli yangilandi!**\n\n"
                f"💰 **Yangi narxlar:**\n"
                f"• 1 oy: {price_1m:,} so'm\n"
                f"• 3 oy: {price_3m:,} so'm\n"
                f"• 6 oy: {price_6m:,} so'm\n"
                f"• 12 oy: {price_12m:,} so'm\n\n"
                f"📅 **Yangilangan:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            
            await state.clear()
            
        except ValueError:
            await message.answer("❌ Faqat raqam kiriting!")

    # Premium tavsifni o'zgartirish
    @dp.callback_query(F.data == "premium_description")
    async def edit_premium_description(callback: CallbackQuery, state: FSMContext):
        if callback.from_user.id not in ADMIN_IDS:
            await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
            return
        
        await callback.message.edit_text(
            "📝 **Premium obuna tavsifini o'zgartirish**\n\n"
            "Yangi tavsifni yozing:\n\n"
            "📄 **Hozirgi tavsif:** Premium obuna: Majburiy obuna talab etilmaydi\n\n"
            "❌ **Bekor qilish:** /cancel"
        )
        
        await state.set_state(PremiumStates.waiting_for_description)

    @dp.message(PremiumStates.waiting_for_description)
    async def get_premium_description(message: Message, state: FSMContext):
        if message.from_user.id not in ADMIN_IDS:
            return
            
        if message.text and message.text.lower() in ['/cancel', 'cancel']:
            await message.answer("❌ **Tavsif o'zgartirish bekor qilindi**")
            await state.clear()
            return
        
        if not message.text:
            await message.answer("❌ Iltimos, tavsifni matn ko'rinishida kiriting!")
            return
            
        new_description = message.text.strip()
        if len(new_description) < 10:
            await message.answer("❌ Tavsif kamida 10 ta belgi bo'lishi kerak!")
            return
        
        await db.update_premium_description(new_description)
        
        await message.answer(
            f"✅ **Premium tavsifi muvaffaqiyatli o'zgartirildi!**\n\n"
            f"📝 **Yangi tavsif:** {new_description}\n\n"
            f"📅 **O'zgartirilgan:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        await state.clear()

    # Premium holatni almashtirish
    @dp.callback_query(F.data == "premium_toggle")
    async def toggle_premium(callback: CallbackQuery):
        if callback.from_user.id not in ADMIN_IDS:
            await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
            return
        
        premium_settings = await db.get_premium_settings()
        new_status = not premium_settings['is_enabled']
        
        await db.toggle_premium_status(new_status)
        
        status_text = "yoqildi" if new_status else "o'chirildi"
        await callback.answer(f"✅ Premium obuna {status_text}!", show_alert=True)
        
        # Yangilangan ma'lumotlarni ko'rsatish
        await show_premium_management(callback)

    # Premium statistika
    @dp.callback_query(F.data == "premium_stats")
    async def show_premium_stats(callback: CallbackQuery):
        if callback.from_user.id not in ADMIN_IDS:
            await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
            return
        
        premium_users_count = await db.get_premium_users_count()
        premium_settings = await db.get_premium_settings()
        
        text = f"📊 **Premium Statistika**\n\n"
        text += f"👥 **Faol premium foydalanuvchilar:** {premium_users_count} ta\n"
        text += f"💎 **Premium holati:** {'🟢 Faol' if premium_settings['is_enabled'] else '🔴 Faol emas'}\n\n"
        text += f"💰 **Joriy narxlar:**\n"
        text += f"• 1 oy: {premium_settings['price_1month']:,} so'm\n"
        text += f"• 3 oy: {premium_settings['price_3months']:,} so'm\n"  
        text += f"• 6 oy: {premium_settings['price_6months']:,} so'm\n"
        text += f"• 12 oy: {premium_settings['price_12months']:,} so'm\n\n"
        text += f"📅 **Oxirgi yangilanish:** Premium tizimi faol"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_premium")]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard)

    # Karta boshqaruvi menu
    @dp.callback_query(F.data == "manage_cards")
    async def show_card_management(callback: CallbackQuery):
        if callback.from_user.id not in ADMIN_IDS:
            await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
            return
        
        cards = await db.get_active_cards()
        
        text = "💳 **Karta Boshqaruvi**\n\n"
        if cards:
            text += "📋 **Faol kartalar:**\n"
            for i, card in enumerate(cards, 1):
                text += f"{i}. {card['card_number']} - {card['card_holder_name']}\n"
        else:
            text += "❌ **Hech qanday faol karta yo'q**"
        
        await callback.message.edit_text(
            text,
            reply_markup=get_card_management_keyboard()
        )

    # Karta almashtirish
    @dp.callback_query(F.data == "replace_card")
    async def show_card_replacement(callback: CallbackQuery):
        if callback.from_user.id not in ADMIN_IDS:
            await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
            return
        
        cards = await db.get_active_cards()
        
        text = "🔄 **Karta Almashtirish**\n\n"
        
        if cards:
            text += "📋 **Hozirgi faol kartalar:**\n"
            for i, card in enumerate(cards, 1):
                masked_card = card['card_number'][:4] + " **** **** " + card['card_number'][-4:]
                text += f"🔹 {masked_card}\n"
                text += f"   👤 {card['card_holder_name']}\n"
                text += f"   📅 {card['added_date'][:10]}\n\n"
        else:
            text += "❌ **Hech qanday faol karta yo'q**\n\n"
        
        text += "➕ **Yangi karta qo'shish uchun 'Karta qo'shish' tugmasini bosing**"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Yangi karta qo'shish", callback_data="add_card")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="manage_cards")]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard)

    # Kartalar ro'yxati
    @dp.callback_query(F.data == "list_cards")
    async def show_cards_list(callback: CallbackQuery):
        if callback.from_user.id not in ADMIN_IDS:
            await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
            return
        
        cards = await db.get_active_cards()
        
        text = "📋 **Barcha Kartalar Ro'yxati**\n\n"
        
        if cards:
            for i, card in enumerate(cards, 1):
                text += f"🔹 **Karta #{i}**\n"
                text += f"   💳 Raqam: `{card['card_number']}`\n"
                text += f"   👤 Egasi: {card['card_holder_name']}\n"
                text += f"   📅 Qo'shilgan: {card['added_date'][:10]}\n"
                text += f"   🟢 Holat: {'Faol' if card['is_active'] else 'Faol emas'}\n\n"
        else:
            text += "❌ **Hech qanday karta topilmadi**"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="manage_cards")]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard)

    # Karta qo'shish
    @dp.callback_query(F.data == "add_card")
    async def add_card_start(callback: CallbackQuery, state: FSMContext):
        if callback.from_user.id not in ADMIN_IDS:
            await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
            return
        
        await callback.message.edit_text(
            "💳 **To'lov kartasi qo'shish**\n\n"
            "📋 **1-qadam: Karta raqamini kiriting**\n"
            "Masalan: `8600 1234 5678 9012`\n\n"
            "❌ **Bekor qilish:** /cancel"
        )
        
        await state.set_state(CardStates.waiting_for_card_number)

    @dp.message(CardStates.waiting_for_card_number)
    async def get_card_number(message: Message, state: FSMContext):
        if message.from_user.id not in ADMIN_IDS:
            return
            
        if message.text and message.text.lower() in ['/cancel', 'cancel']:
            await message.answer("❌ **Karta qo'shish bekor qilindi**")
            await state.clear()
            return
        
        if not message.text:
            await message.answer("❌ Iltimos, karta raqamini kiriting!")
            return
            
        card_number = message.text.strip()
        
        # Karta raqami validatsiyasi (16 raqam yoki probel bilan)
        clean_number = card_number.replace(' ', '').replace('-', '')
        if not clean_number.isdigit() or len(clean_number) != 16:
            await message.answer("❌ Karta raqami 16 ta raqamdan iborat bo'lishi kerak!\nMasalan: 8600 1234 5678 9012")
            return
            
        await state.update_data(card_number=card_number)
        
        await message.answer(
            f"✅ **Karta raqami:** {card_number}\n\n"
            f"📋 **2-qadam: Karta egasining ism-familyasini kiriting**\n"
            f"Masalan: `ANVAR KARIMOV`"
        )
        
        await state.set_state(CardStates.waiting_for_card_holder_name)

    @dp.message(CardStates.waiting_for_card_holder_name)
    async def get_card_holder_name(message: Message, state: FSMContext):
        if message.from_user.id not in ADMIN_IDS:
            return
            
        if not message.text:
            await message.answer("❌ Iltimos, ism-familyani kiriting!")
            return
            
        card_holder_name = message.text.strip().upper()
        
        if len(card_holder_name) < 3:
            await message.answer("❌ Ism-familya kamida 3 ta belgidan iborat bo'lishi kerak!")
            return
        
        data = await state.get_data()
        card_number = data['card_number']
        
        # Kartani bazaga qo'shish
        await db.add_payment_card(card_number, card_holder_name)
        
        await message.answer(
            f"✅ **To'lov kartasi muvaffaqiyatli qo'shildi!**\n\n"
            f"💳 **Karta raqami:** {card_number}\n"
            f"👤 **Karta egasi:** {card_holder_name}\n\n"
            f"📅 **Qo'shilgan:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"ℹ️ Endi foydalanuvchilar ushbu kartaga to'lov qilishlari mumkin."
        )
        
        await state.clear()

    # Kutilayotgan to'lovlar
    @dp.callback_query(F.data == "pending_payments")
    async def show_pending_payments(callback: CallbackQuery):
        if callback.from_user.id not in ADMIN_IDS:
            await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
            return
        
        pending_payments = await db.get_pending_payments()
        
        if not pending_payments:
            await callback.message.edit_text(
                "📋 **Kutilayotgan to'lovlar**\n\n"
                "❌ Hozircha kutilayotgan to'lovlar yo'q.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_premium")]
                ])
            )
            return
        
        text = f"📋 **Kutilayotgan to'lovlar ({len(pending_payments)} ta)**\n\n"
        
        for payment in pending_payments[:5]:  # Faqat 5 tasini ko'rsatish
            username = f"@{payment['username']}" if payment['username'] else "Username yo'q"
            months_map = {'1m': '1 oy', '3m': '3 oy', '6m': '6 oy', '12m': '12 oy'}
            period = months_map.get(payment['subscription_type'], payment['subscription_type'])
            
            text += f"👤 **{payment['first_name']}** ({username})\n"
            text += f"💰 {payment['amount']:,} so'm - {period}\n"
            text += f"📅 {payment['created_date'][:16]}\n\n"
        
        if len(pending_payments) > 5:
            text += f"➕ Yana {len(pending_payments) - 5} ta to'lov..."
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Yangilash", callback_data="pending_payments")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_premium")]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard)

    # To'lov cheki qabul qilish
    @dp.message(PaymentStates.waiting_for_receipt)
    async def receive_payment_receipt(message: Message, state: FSMContext):
        if not (message.photo or message.document):
            await message.answer("❌ Iltimos, to'lov chekining rasmini yuboring!")
            return
        
        data = await state.get_data()
        payment_amount = data.get('payment_amount')
        subscription_type = data.get('subscription_type')
        period_text = data.get('period_text')
        
        # To'lov ma'lumotlarini bazaga saqlash
        payment_id = await db.add_premium_payment(
            message.from_user.id,
            payment_amount,
            subscription_type
        )
        
        # Tekshiruv yaratish
        verification_id = await db.add_payment_verification(
            message.from_user.id,
            payment_id,
            message.message_id
        )
        
        # Foydalanuvchiga javob
        await message.answer(
            f"✅ **Chekingiz adminga yuborildi!**\n\n"
            f"💰 **Summa:** {payment_amount:,} so'm\n"
            f"📋 **Tarif:** {period_text}\n\n"
            f"⏳ **Admin tasdiqlashini kuting...**\n\n"
            f"📞 Tez orada chekingiz tekshiriladi va to'lov tasdiqlanadi.\n"
            f"📱 Premium obuna faollashgach avtomatik xabar beriladi!"
        )
        
        # Adminlarga forward qilish
        for admin_id in ADMIN_IDS:
            try:
                username = message.from_user.username
                username_text = f"@{username}" if username else "Username yo'q"
                
                admin_text = f"� **YANGI TO'LOV CHEKI!**\n\n"
                admin_text += f"👤 **Foydalanuvchi:** {message.from_user.first_name}\n"
                admin_text += f"📱 **Username:** {username_text}\n"
                admin_text += f"🆔 **User ID:** `{message.from_user.id}`\n\n"
                admin_text += f"💰 **To'lov summasi:** {payment_amount:,} so'm\n"
                admin_text += f"📋 **Premium tarif:** {period_text}\n"
                admin_text += f"📅 **Yuborilgan vaqt:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                admin_text += f"⬆️ **Yuqorida to'lov cheki rasmi**\n"
                admin_text += f"⬇️ **Quyida tasdiqlash tugmalari**"
                
                # Chekni forward qilish
                await message.forward(admin_id)
                
                # Admin tugmalari bilan xabar yuborish
                await bot.send_message(
                    admin_id,
                    admin_text,
                    reply_markup=get_payment_verification_keyboard(verification_id)
                )
                
            except Exception as e:
                print(f"Admin {admin_id} ga xabar yuborishda xatolik: {e}")
        
        await state.clear()

    # To'lovni tasdiqlash
    @dp.callback_query(F.data.startswith("approve_payment_"))
    async def approve_payment_handler(callback: CallbackQuery):
        if callback.from_user.id not in ADMIN_IDS:
            await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
            return
        
        verification_id = int(callback.data.split("_")[-1])
        
        # To'lov ma'lumotlarini olish
        payment_info = await db.get_payment_by_verification_id(verification_id)
        
        if not payment_info:
            await callback.answer("❌ To'lov ma'lumotlari topilmadi!", show_alert=True)
            return
        
        # To'lovni tasdiqlash
        await db.approve_payment(verification_id, callback.from_user.id)
        
        # Premium obunasini faollashtirish
        months_map = {'1m': 1, '3m': 3, '6m': 6, '12m': 12}
        months = months_map.get(payment_info['subscription_type'], 1)
        
        await db.add_user_premium(
            payment_info['user_id'],
            payment_info['subscription_type'],
            months
        )
        
        # Foydalanuvchiga xabar
        try:
            period_map = {'1m': '1 oy', '3m': '3 oy', '6m': '6 oy', '12m': '12 oy'}
            period_text = period_map.get(payment_info['subscription_type'], payment_info['subscription_type'])
            
            await bot.send_message(
                payment_info['user_id'],
                f"🎉 **To'lovingiz tasdiqlandi!**\n\n"
                f"💎 **Premium obuna faollashdi!**\n"
                f"📋 **Tarif:** {period_text}\n"
                f"💰 **Summa:** {payment_info['amount']:,} so'm\n\n"
                f"🎬 Endi siz majburiy obunasiz kinolar ko'ra olasiz!\n"
                f"⚡ To'g'ridan-to'g'ri /start bosing!"
            )
        except:
            pass
        
        # Admin xabari
        await callback.message.edit_text(
            f"✅ **To'lov tasdiqlandi!**\n\n"
            f"👤 **User ID:** {payment_info['user_id']}\n"
            f"💰 **Summa:** {payment_info['amount']:,} so'm\n"
            f"📋 **Tarif:** {payment_info['subscription_type']}\n\n"
            f"🎉 Premium obuna faollashtirildi!"
        )

    # To'lovni rad etish
    @dp.callback_query(F.data.startswith("reject_payment_"))
    async def reject_payment_handler(callback: CallbackQuery):
        if callback.from_user.id not in ADMIN_IDS:
            await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
            return
        
        verification_id = int(callback.data.split("_")[-1])
        
        # To'lov ma'lumotlarini olish
        payment_info = await db.get_payment_by_verification_id(verification_id)
        
        if not payment_info:
            await callback.answer("❌ To'lov ma'lumotlari topilmadi!", show_alert=True)
            return
        
        # To'lovni rad etish
        await db.reject_payment(verification_id, callback.from_user.id)
        
        # Foydalanuvchiga xabar
        try:
            await bot.send_message(
                payment_info['user_id'],
                f"❌ **To'lovingiz rad etildi!**\n\n"
                f"💰 **Summa:** {payment_info['amount']:,} so'm\n\n"
                f"📞 **Sababi:**\n"
                f"• Noto'g'ri summa\n"
                f"• Chek aniq emas\n"
                f"• Boshqa sabab\n\n"
                f"💡 **Qayta urinib ko'ring yoki admin bilan bog'laning.**"
            )
        except:
            pass
        
        # Admin xabari
        await callback.message.edit_text(
            f"❌ **To'lov rad etildi!**\n\n"
            f"👤 **User ID:** {payment_info['user_id']}\n"
            f"💰 **Summa:** {payment_info['amount']:,} so'm\n\n"
            f"📞 Foydalanuvchiga xabar yuborildi."
        )

    # Kanal ID topish va sozlash yo'riqnomasi
    @dp.message(Command("channel_setup"))
    async def channel_setup_guide(message: Message):
        if message.from_user.id not in ADMIN_IDS:
            await message.answer("❌ Sizda admin huquqlari yo'q!")
            return
        
        guide_text = f"""
🔧 **Baza Kanal Sozlash Yo'riqnomasi**

📺 **Hozirgi holat:**
• Kanal linki: {BASE_CHANNEL_LINK}
• Kanal ID: {BASE_CHANNEL_ID or 'Sozlanmagan'}

📋 **Kanal ID topish qadamlari:**

1️⃣ **Kanalga botni qo'shing:**
   • Kanalga boring
   • Bot @JahonFilmlari_bot ni qo'shing
   • Admin huquq bering

2️⃣ **Kanal ID topish:**
   • @userinfobot ga boring
   • Kanal linkini yuboring: {BASE_CHANNEL_LINK}
   • ID ni olasiz: -1001234567890

3️⃣ **config.py ni yangilang:**
```python
BASE_CHANNEL_ID = -1001234567890  # Haqiqiy ID
```

4️⃣ **Botni qayta ishga tushiring**

🔍 **ID tekshirish:**
• Private kanal: -100 bilan boshlanadi
• Public kanal: @ bilan
• Group: - bilan boshlanadi

📞 **Yordam kerak bo'lsa:**
• Screenshot yuborishingiz mumkin
• Qadama-qadam yo'l ko'rsataman
        """
        
        await message.answer(guide_text)

    # Kanal ID tekshirish (agar mavjud bo'lsa)  
    @dp.callback_query(F.data == "test_channel")
    async def test_base_channel(callback: CallbackQuery):
        if callback.from_user.id not in ADMIN_IDS:
            await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
            return
        
        if not BASE_CHANNEL_ID:
            await callback.message.edit_text(
                "❌ **Baza kanal ID sozlanmagan!**\n\n"
                f"Yo'riqnoma uchun: /channel_setup"
            )
            return
        
        try:
            # Bot haqida ma'lumot
            bot_info = await bot.get_me()
            
            # Kanal tekshiruvi
            try:
                chat_info = await bot.get_chat(BASE_CHANNEL_ID)
                bot_member = await bot.get_chat_member(chat_id=BASE_CHANNEL_ID, user_id=bot_info.id)
                
                status_emoji = "✅" if bot_member.status in ['administrator', 'creator'] else "❌"
                
                info_text = f"🔍 **Baza kanal holati:**\n\n"
                info_text += f"📺 **Kanal:** {chat_info.title}\n"
                info_text += f"🆔 **ID:** `{chat_info.id}`\n"
                info_text += f"👤 **Username:** @{chat_info.username or 'Yoq'}\n"
                info_text += f"🤖 **Bot status:** {status_emoji} {bot_member.status}\n\n"
                
                if bot_member.status in ['administrator', 'creator']:
                    info_text += f"✅ **Tayyor!** Kinolar yuboriladi."
                else:
                    info_text += f"❌ **Bot admin emas!** Admin qiling."
                    
            except Exception as chat_error:
                info_text = f"❌ **Xatolik!**\n\n"
                info_text += f"🆔 **ID:** `{BASE_CHANNEL_ID}`\n"
                info_text += f"❌ **Sabab:** {chat_error}\n\n"
                info_text += f"**Hal qilish:**\n"
                info_text += f"• Bot kanalga qo'shilganini tekshiring\n"
                info_text += f"• ID to'g'riligini tekshiring\n"
                info_text += f"• /channel_setup - yo'riqnoma"
                
        except Exception as e:
            info_text = f"❌ **Umumiy xatolik:** {e}"
        
        await callback.message.edit_text(info_text)

    # Kinolar ro'yxati ko'rsatish
    @dp.callback_query(F.data == "movies_list")
    async def show_movies_list(callback: CallbackQuery):
        if callback.from_user.id not in ADMIN_IDS:
            await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
            return
        
        movies = await db.get_all_movies()
        
        if not movies:
            text = "❌ Hozircha kinolar yo'q.\n\nBirinchi kinoni qo'shish uchun ➕ Kino qo'shish tugmasini bosing."
        else:
            text = f"🎬 **Barcha kinolar ({len(movies)} ta):**\n\n"
            
            # Faqat birinchi 20 tani ko'rsatish
            display_movies = movies[:20]
            
            for i, movie in enumerate(display_movies, 1):
                text += f"{i}. **{movie['title']}**\n"
                text += f"   🆔 Kod: `{movie['code']}`\n"
                text += f"   👁‍🗨 Ko'rishlar: {movie['views']}\n"
                text += f"   📅 Qo'shilgan: {movie['added_date'][:10]}\n\n"
            
            if len(movies) > 20:
                text += f"... va yana {len(movies) - 20} ta kino"
        
        from utils.keyboard import get_back_keyboard
        await callback.message.edit_text(
            text,
            reply_markup=get_back_keyboard("admin_movies")
        )

    # Top kinolar ko'rsatish
    @dp.callback_query(F.data == "top_movies")
    async def show_top_movies(callback: CallbackQuery):
        if callback.from_user.id not in ADMIN_IDS:
            await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
            return
        
        movies = await db.get_top_movies(10)
        
        if not movies:
            text = "❌ Hozircha kinolar yo'q.\n\nBirinchi kinoni qo'shish uchun ➕ Kino qo'shish tugmasini bosing."
        else:
            text = "🏆 **Top 10 eng ko'p ko'rilgan kinolar:**\n\n"
            
            for i, movie in enumerate(movies, 1):
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                text += f"{medal} **{movie['title']}**\n"
                text += f"   🆔 Kod: `{movie['code']}`\n"
                text += f"   👁‍🗨 Ko'rishlar: {movie['views']}\n\n"
        
        from utils.keyboard import get_back_keyboard
        await callback.message.edit_text(
            text,
            reply_markup=get_back_keyboard("admin_movies")
        )

    # Kino o'chirish - ro'yxat
    @dp.callback_query(F.data == "delete_movie")
    async def delete_movie_list(callback: CallbackQuery):
        if callback.from_user.id not in ADMIN_IDS:
            await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
            return
        
        movies = await db.get_all_movies()
        
        if not movies:
            await callback.answer("❌ O'chiradigan kinolar yo'q!", show_alert=True)
            return
        
        # Faqat birinchi 10 tani ko'rsatish
        display_movies = movies[:10]
        
        keyboard = []
        for movie in display_movies:
            keyboard.append([
                InlineKeyboardButton(
                    text=f"🗑 {movie['title']} ({movie['code']})",
                    callback_data=f"delete_mv_{movie['id']}"
                )
            ])
        
        keyboard.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_movies")])
        
        await callback.message.edit_text(
            f"🗑 **Kino o'chirish**\n\n"
            f"O'chiradigan kinoni tanlang:\n"
            f"(Ko'rsatilgan: {len(display_movies)}/{len(movies)})",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )

    # Kino o'chirishni tasdiqlash
    @dp.callback_query(F.data.startswith("delete_mv_"))
    async def confirm_delete_movie(callback: CallbackQuery):
        if callback.from_user.id not in ADMIN_IDS:
            await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
            return
            
        movie_id = callback.data.split("_")[-1]
        
        # Kino ma'lumotlarini olish
        movies = await db.get_all_movies()
        movie = None
        for m in movies:
            if str(m['id']) == movie_id:
                movie = m
                break
        
        if not movie:
            await callback.answer("❌ Kino topilmadi!", show_alert=True)
            return
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Ha, o'chirish", callback_data=f"confirm_delete_mv_{movie_id}"),
                InlineKeyboardButton(text="❌ Yo'q", callback_data="delete_movie")
            ]
        ])
        
        await callback.message.edit_text(
            f"⚠️ **Ogohlanitirish!**\n\n"
            f"Quyidagi kinoni o'chirishni tasdiqlaysizmi?\n\n"
            f"🎬 **{movie['title']}**\n"
            f"🆔 Kod: `{movie['code']}`\n"
            f"👁‍🗨 Ko'rishlar: {movie['views']}\n\n"
            f"❗️ Bu amalni bekor qilib bo'lmaydi!",
            reply_markup=keyboard
        )

    # Kinoni o'chirishni amalga oshirish
    @dp.callback_query(F.data.startswith("confirm_delete_mv_"))
    async def delete_movie_confirm(callback: CallbackQuery):
        if callback.from_user.id not in ADMIN_IDS:
            await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
            return
            
        movie_id = int(callback.data.split("_")[-1])
        
        # Kino ma'lumotlarini olish
        movies = await db.get_all_movies()
        movie = None
        for m in movies:
            if m['id'] == movie_id:
                movie = m
                break
        
        # Kinoni o'chirish
        success = await db.delete_movie(movie_id)
        
        if success and movie:
            text = f"✅ **Kino muvaffaqiyatli o'chirildi!**\n\n"
            text += f"🎬 Nomi: {movie['title']}\n"
            text += f"🆔 Kodi: {movie['code']}"
        else:
            text = "❌ Kinoni o'chirishda xatolik yuz berdi!"
        
        from utils.keyboard import get_back_keyboard
        await callback.message.edit_text(
            text,
            reply_markup=get_back_keyboard("admin_movies")
        )

    # Kanallar ro'yxati ko'rsatish
    @dp.callback_query(F.data == "channels_list")
    async def show_channels_list(callback: CallbackQuery):
        if callback.from_user.id not in ADMIN_IDS:
            await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
            return
        
        channels = await db.get_all_channels()
        
        if not channels:
            text = "❌ Hozircha majburiy obuna kanallari yo'q.\n\n"
            text += "Kanal qo'shish uchun ➕ Kanal qo'shish tugmasini bosing."
        else:
            text = f"📺 **Majburiy obuna kanallari ({len(channels)} ta):**\n\n"
            
            for i, channel in enumerate(channels, 1):
                text += f"{i}. **{channel['channel_name']}**\n"
                text += f"   🆔 ID: `{channel['channel_id']}`\n"
                
                if channel['channel_username']:
                    text += f"   📱 Username: @{channel['channel_username']}\n"
                else:
                    text += f"   📱 Username: Yo'q\n"
                    
                text += f"   📅 Qo'shilgan: {channel['added_date'][:10]}\n\n"
        
        from utils.keyboard import get_back_keyboard
        await callback.message.edit_text(
            text,
            reply_markup=get_back_keyboard("admin_channels")
        )

    # Kanal qo'shish - YANGI
    @dp.callback_query(F.data == "add_channel")
    async def add_channel_new_start(callback: CallbackQuery, state: FSMContext):
        if callback.from_user.id not in ADMIN_IDS:
            await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
            return
        await callback.message.edit_text(
            "➕ **Yangi kanal qo'shish**\n\n"
            "1️⃣ **Kanal nomini kiriting:**\n"
            "Masalan: `Kino Kanali` yoki `Yangiliklar`\n\n"
            "2️⃣ **Keyin, kanal postidan biror postni forward qilib yuboring!**\n"
            "(Kanalga bot admin bo'lishi shart)\n\n"
            "❌ **Bekor qilish:** /cancel"
        )
        await state.set_state(ChannelStates.waiting_for_channel_name)

    @dp.message(ChannelStates.waiting_for_channel_name)
    async def add_channel_new_get_name(message: Message, state: FSMContext):
        if message.from_user.id not in ADMIN_IDS:
            return
        if not message.text:
            await message.answer("❌ Iltimos, kanal nomini yozing!")
            return
        channel_name = message.text.strip()
        if len(channel_name) < 2:
            await message.answer("❌ Kanal nomi kamida 2 ta harf bo'lishi kerak!")
            return
        await state.update_data(channel_name=channel_name)
        await message.answer(
            f"✅ **1-qadam bajarildi!**\n"
            f"📺 Kanal nomi: `{channel_name}`\n\n"
            f"2️⃣ **Endi, qo'shmoqchi bo'lgan kanaldan biror postni forward qilib yuboring!**\n"
            f"(Kanalga bot admin bo'lishi shart)\n\n"
            f"❌ **Bekor qilish:** /cancel"
        )
        await state.set_state(ChannelStates.waiting_for_channel_forward)

    @dp.message(ChannelStates.waiting_for_channel_forward)
    async def add_channel_get_forward(message: Message, state: FSMContext):
        if message.from_user.id not in ADMIN_IDS:
            return
        if not message.forward_from_chat or message.forward_from_chat.type != "channel":
            await message.answer("❌ Iltimos, kanal postini forward qilib yuboring!")
            return
        channel_chat = message.forward_from_chat
        channel_id = channel_chat.id
        channel_username = channel_chat.username
        data = await state.get_data()
        channel_name = data.get("channel_name")
        # Kanalni bazaga qo'shish
        success = await db.add_channel(channel_id, channel_name, channel_username)
        if success:
            text = f"✅ **Kanal muvaffaqiyatli qo'shildi!**\n\n"
            text += f"📺 **Nomi:** {channel_name}\n"
            text += f"🆔 **ID:** `{channel_id}`\n"
            text += f"📱 **Username:** @{channel_username if channel_username else 'Yoq'}\n\n"
            text += f"ℹ️ **Eslatma:**\n"
            text += f"• Bot kanalga admin qilib qo'shilganini tekshiring\n"
            text += f"• Foydalanuvchilar endi obuna bo'lishi shart"
        else:
            text = f"❌ **Bu kanal allaqachon mavjud!**\n\nBoshqa kanal kiriting yoki mavjud kanalni o'chiring."
        await message.answer(text)
        await state.clear()



    @dp.message(ChannelStates.waiting_for_channel_username)
    # endi bu handler kerak emas, forward orqali qo'shiladi

    # Kanal o'chirish
    @dp.callback_query(F.data == "delete_channel") 
    async def delete_channel_list(callback: CallbackQuery):
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
            f"🗑 **Majburiy obuna kanalini o'chirish**\n\n"
            f"O'chiradigan kanalni tanlang:\n"
            f"Ko'rsatilgan: {len(channels)} ta kanal",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )

    # Kanal o'chirishni tasdiqlash  
    @dp.callback_query(F.data.startswith("delete_ch_"))
    async def confirm_delete_channel(callback: CallbackQuery):
        if callback.from_user.id not in ADMIN_IDS:
            await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
            return
            
        channel_db_id = callback.data.split("_")[-1]
        
        # Kanal ma'lumotlarini olish
        channels = await db.get_all_channels()
        channel = None
        for ch in channels:
            if str(ch['id']) == channel_db_id:
                channel = ch
                break
        
        if not channel:
            await callback.answer("❌ Kanal topilmadi!", show_alert=True)
            return
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Ha, o'chirish", callback_data=f"confirm_delete_ch_{channel_db_id}"),
                InlineKeyboardButton(text="❌ Yo'q", callback_data="delete_channel")
            ]
        ])
        
        await callback.message.edit_text(
            f"⚠️ **Ogohlantirish!**\n\n"
            f"Quyidagi kanalni majburiy obuna ro'yxatidan o'chirishni tasdiqlaysizmi?\n\n"
            f"📺 **{channel['channel_name']}**\n"
            f"🆔 ID: `{channel['channel_id']}`\n"
            f"📱 Username: @{channel['channel_username'] or 'Yoq'}\n\n"
            f"❗️ Bu amalni bekor qilib bo'lmaydi!\n"
            f"Foydalanuvchilar bu kanalga obuna bo'lmasdan ham bot ishlatishadi.",
            reply_markup=keyboard
        )

    # Kanalni o'chirishni amalga oshirish
    @dp.callback_query(F.data.startswith("confirm_delete_ch_"))
    async def delete_channel_confirm(callback: CallbackQuery):
        if callback.from_user.id not in ADMIN_IDS:
            await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
            return
            
        channel_db_id = int(callback.data.split("_")[-1])
        
        # Kanal ma'lumotlarini olish (o'chirishdan oldin)
        channels = await db.get_all_channels()
        channel = None
        for ch in channels:
            if ch['id'] == channel_db_id:
                channel = ch
                break
        
        # Kanalni o'chirish
        success = await db.delete_channel(channel_db_id)
        
        if success and channel:
            text = f"✅ **Kanal muvaffaqiyatli o'chirildi!**\n\n"
            text += f"📺 Nomi: {channel['channel_name']}\n"
            text += f"🆔 ID: `{channel['channel_id']}`\n\n"
            text += f"ℹ️ Endi foydalanuvchilar bu kanalga obuna bo'lmasdan ham bot ishlatishadi."
        else:
            text = "❌ Kanalni o'chirishda xatolik yuz berdi!"
        
        from utils.keyboard import get_back_keyboard
        await callback.message.edit_text(
            text,
            reply_markup=get_back_keyboard("admin_channels")
        )

    @dp.callback_query(F.data == "admin_back")
    async def admin_back(callback: CallbackQuery):
        if callback.from_user.id not in ADMIN_IDS:
            await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
            return
        
        await callback.message.edit_text(
            "👑 **Admin Panel**\n\nKerakli bo'limni tanlang:",
            reply_markup=get_admin_panel_keyboard()
        )

    # Obuna tekshirish callback
    @dp.callback_query(F.data == "check_subscription")
    async def check_subscription_callback(callback: CallbackQuery):
        """Obunani tekshirish callback handleri"""
        # Majburiy obuna kanallarini olish
        channels = await db.get_all_channels()
        
        if not channels:
            await callback.message.edit_text(SUBSCRIBED_TEXT)
            await callback.answer()
            return
        
        # Obunani tekshirish
        is_subscribed = await check_user_subscription(bot, callback.from_user.id, channels, db)
        
        if is_subscribed:
            await callback.message.edit_text(SUBSCRIBED_TEXT)
            await callback.answer("✅ Obuna tasdiqlandi!", show_alert=True)
            
            # Faollikni yangilash
            await db.update_user_activity(callback.from_user.id)
        else:
            from config import NOT_SUBSCRIBED_TEXT
            await callback.answer(NOT_SUBSCRIBED_TEXT, show_alert=True)

    # Matn xabarlarini qayta ishlash
    @dp.message()
    async def handle_movie_request(message: Message, state: FSMContext):
        """Kino kodi bilan ishlash handleri"""
        # FSM holatini tekshirish - agar foydalanuvchi FSM holatida bo'lsa, ignore qilish
        current_state = await state.get_state()
        if current_state is not None:
            return
        
        # Agar xabar kino kodi bo'lmasa, e'tibor bermaslik
        if not message.text or not is_movie_code_valid(message.text.strip()):
            return
        
        # Faollikni yangilash
        await db.update_user_activity(message.from_user.id)
        
        # Premium obuna muddatini tekshirish
        premium_info = await db.check_premium_expiry(message.from_user.id)
        
        # Agar premium muddati tugagan bo'lsa
        if premium_info['has_premium'] and premium_info['remaining_days'] <= 0:
            # Premium obunani o'chirish
            await db.remove_user_premium(message.from_user.id)
            
            username = message.from_user.first_name or "Foydalanuvchi"
            await message.answer(
                f"⚠️ **Premium obuna tugadi!**\n\n"
                f"Hurmatli {username}, premium obunangizning muddati tugagan.\n\n"
                f"🔄 **Yangi obuna uchun:**\n"
                f"💎 Premium obunani qayta faollashtiring\n"
                f"🆓 Yoki majburiy obuna orqali davom eting",
                reply_markup=get_welcome_choice_keyboard()
            )
            return
        
        # Agar premium faol bo'lsa, majburiy obunani o'tkazib yuborish
        if premium_info['has_premium']:
            # Premium foydalanuvchi uchun to'g'ridan-to'g'ri kino berish
            pass
        else:
            # Majburiy obuna kanallarini olish
            channels = await db.get_all_channels()
            
            # Agar kanallar mavjud bo'lsa, obunani tekshirish
            if channels:
                is_subscribed = await check_user_subscription(bot, message.from_user.id, channels, db)
                
                if not is_subscribed:
                    username = message.from_user.first_name or "Foydalanuvchi"
                    welcome_message = WELCOME_TEXT.format(username=username)
                    
                    # Premium obuna holatini tekshirish
                    premium_settings = await db.get_premium_settings()
                    show_premium = premium_settings['is_enabled']
                    
                    await message.answer(
                        welcome_message,
                        reply_markup=get_subscription_keyboard(channels, show_premium)
                    )
                    return
        
        # Premium muddati tugash arafasida ogohlantrish
        if premium_info['has_premium'] and premium_info['is_expiring_soon']:
            remaining = premium_info['remaining_days']
            username = message.from_user.first_name or "Foydalanuvchi"
            warning_text = (
                f"⚠️ **Premium obuna tugash arafasida!**\n\n"
                f"Hurmatli {username}, premium obunangiz {remaining} kundan so'ng tugaydi.\n\n"
                f"🔄 **Obunani yangilash uchun:**\n"
                f"💎 Premium obuna bo'limiga o'ting\n\n"
            )
            
            # Ogohlantirishni faqat 1 marta yuborish
            await message.answer(warning_text, reply_markup=get_welcome_choice_keyboard())
        
        # Kino kodini olish
        movie_code = message.text.strip().upper()
        
        # Kinoni bazadan qidirish
        movie = await db.get_movie_by_code(movie_code)
        
        if movie:
            try:
                # Kinoni yuborish (barcha foydalanuvchilar bir xil formatda)
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

    # Premium obuna ko'rsatish
    @dp.callback_query(F.data == "show_premium")
    async def show_premium_options(callback: CallbackQuery):
        premium_settings = await db.get_premium_settings()
        
        if not premium_settings['is_enabled']:
            await callback.answer("❌ Premium obuna hozircha mavjud emas!", show_alert=True)
            return
        
        # Foydalanuvchi premium obunasini tekshirish
        has_premium = await db.check_user_premium(callback.from_user.id)
        
        if has_premium:
            await callback.answer("✅ Sizda allaqachon Premium obuna mavjud!", show_alert=True)
            return
        
        text = f"💎 **Premium Obuna**\n\n"
        text += f"📝 **Afzalliklari:**\n{premium_settings['description']}\n\n"
        text += f"💰 **Narxlar:**\n\n"
        text += f"1️⃣ **1 oy** - {premium_settings['price_1month']:,} so'm\n"
        text += f"3️⃣ **3 oy** - {premium_settings['price_3months']:,} so'm\n"
        text += f"6️⃣ **6 oy** - {premium_settings['price_6months']:,} so'm\n"
        text += f"🔥 **12 oy** - {premium_settings['price_12months']:,} so'm\n\n"
        text += f"💳 **To'lov:** Admin bilan bog'laning"
        
        await callback.message.edit_text(
            text,
            reply_markup=get_premium_subscription_keyboard(premium_settings)
        )

    # Premium obuna xarid qilish
    @dp.callback_query(F.data.startswith("premium_pay_"))
    async def buy_premium(callback: CallbackQuery, state: FSMContext):
        subscription_type = callback.data.split("_")[-1]  # 1m, 3m, 6m, 12m
        
        premium_settings = await db.get_premium_settings()
        
        # Narx va muddat xaritasi
        price_map = {
            "1m": (premium_settings['price_1month'], 1, "1 oy"),
            "3m": (premium_settings['price_3months'], 3, "3 oy"),
            "6m": (premium_settings['price_6months'], 6, "6 oy"),
            "12m": (premium_settings['price_12months'], 12, "12 oy")
        }
        
        if subscription_type not in price_map:
            await callback.answer("❌ Noto'g'ri obuna turi!", show_alert=True)
            return
        
        price, months, period_text = price_map[subscription_type]
        
        # Faol kartalarni olish
        cards = await db.get_active_cards()
        
        if not cards:
            await callback.answer("❌ Hozircha to'lov kartalari mavjud emas!", show_alert=True)
            return
        
        # To'lov ma'lumotlarini ko'rsatish
        text = f"💎 **Premium Obuna To'lovi**\n\n"
        text += f"📋 **Tanlangan tarif:** {period_text}\n"
        text += f"💰 **Narx:** {price:,} so'm\n\n"
        text += f"💳 **To'lov kartasi ma'lumotlari:**\n"
        
        for card in cards:
            text += f"💳 **{card['card_number']}**\n"
            text += f"👤 **{card['card_holder_name']}**\n\n"
        
        text += f"� **To'lov qilish tartibi:**\n"
        text += f"1️⃣ Yuqoridagi kartaga {price:,} so'm o'tkazing\n"
        text += f"2️⃣ To'lov chekini surat qilib oling\n"
        text += f"3️⃣ Chekni shu botga yuboring\n"
        text += f"4️⃣ Admin tasdiqlashini kuting\n\n"
        text += f"⚠️ **Eslatma:** To'lov tasdiqlangach Premium obuna avtomatik faollashadi!"
        
        # To'lov ma'lumotlarini saqlash (pending holatida)
        await db.add_premium_payment(
            callback.from_user.id, 
            price, 
            f"{months}m"
        )
        
        # State ni o'rnatish
        await state.set_state(PaymentStates.waiting_for_receipt)
        await state.set_data({
            'payment_amount': price,
            'subscription_type': f"{months}m",
            'period_text': period_text
        })
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="👤 Admin bilan bog'lanish", url="https://t.me/menejer_1w"),
                InlineKeyboardButton(text="🔙 Orqaga", callback_data="show_premium")
            ]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard)

    # Premium bekor qilish
    @dp.callback_query(F.data == "cancel_premium")
    async def cancel_premium_purchase(callback: CallbackQuery):
        channels = await db.get_all_channels()
        show_premium = False  # Premium tugmasini ko'rsatmaslik
        
        username = callback.from_user.first_name or "Foydalanuvchi"
        welcome_message = WELCOME_TEXT.format(username=username)
        
        await callback.message.edit_text(
            welcome_message,
            reply_markup=get_subscription_keyboard(channels, show_premium)
        )

    # Admin boshqaruvi
    @dp.callback_query(F.data == "admin_management")
    async def admin_management_handler(callback: CallbackQuery):
        if callback.from_user.id not in ADMIN_IDS:
            await callback.answer("❌ Sizda admin huquqlari yo'q!", show_alert=True)
            return

        text = (
            "👑 **Admin Boshqaruvi**\n\n"
            "🔧 **Bot adminlari boshqaruvi:**\n"
            "• Admin qo'shish va o'chirish\n"
            "• Huquqlarni boshqarish\n"
            "• Adminlar ro'yxatini ko'rish\n\n"
            "⚠️ **Diqqat:** Faqat super admin adminlarni boshqara oladi!"
        )
        
        await callback.message.edit_text(
            text,
            reply_markup=get_admin_management_keyboard()
        )

    # Admin huquqlari boshqaruvi
    @dp.callback_query(F.data == "admin_permissions")
    async def admin_permissions_handler(callback: CallbackQuery):
        if callback.from_user.id not in ADMIN_IDS:
            await callback.answer("❌ Sizda admin huquqlari yo'q!", show_alert=True)
            return

        text = (
            "⚙️ **Admin Huquqlari Boshqaruvi**\n\n"
            "Quyidagi huquqlardan birini tanlang yoki admin huquqlarini o'zgartiring.\n\n"
            "🔰 Asosiy - Botni boshqarish\n"
            "📊 Statistika - Foydalanuvchi va kino statistikasi\n"
            "🎬 Kinolar - Kino qo'shish/o'chirish\n"
            "📺 Kanallar - Kanal boshqaruvi\n"
            "📢 Xabar yuborish - Ommaviy xabar\n"
            "💎 Premium - Premium boshqaruvi\n"
        )
        await callback.message.edit_text(
            text,
            reply_markup=get_admin_permissions_keyboard()
        )

    @dp.callback_query(F.data == "admin_list")
    async def admin_list_handler(callback: CallbackQuery):
        if callback.from_user.id not in ADMIN_IDS:
            await callback.answer("❌ Sizda admin huquqlari yo'q!", show_alert=True)
            return

        admins = await db.get_all_admins()
        if not admins:
            text = "📋 **Adminlar ro'yxati**\n\n❌ Hech qanday admin topilmadi."
        else:
            text = f"📋 **Adminlar ro'yxati** ({len(admins)} ta)\n\n"
            for i, admin in enumerate(admins, 1):
                status = "✅ Faol" if admin['is_active'] else "❌ Nofaol"
                username = f"@{admin['username']}" if admin['username'] else "❌ Username yo'q"
                name = admin['first_name'] or "❌ Nom yo'q"
                permissions = admin['permissions'] or "basic"
                text += f"{i}. **{name}** ({username})\n"
                text += f"   🆔 ID: `{admin['user_id']}`\n"
                text += f"   🔐 Huquq: {permissions}\n"
                text += f"   📊 Holat: {status}\n"
                text += f"   📅 Qo'shilgan: {admin['added_date'][:10]}\n\n"
        # Faqat yangilash va orqaga tugmalari
        keyboard = [
            [InlineKeyboardButton(text="🔄 Yangilash", callback_data="admin_list")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_management")]
        ]
        await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))

    @dp.callback_query(F.data == "add_admin")
    async def add_admin_handler(callback: CallbackQuery, state: FSMContext):
        print(f"🔍 DEBUG: add_admin callback ishga tushdi. User: {callback.from_user.id}")
        
        if callback.from_user.id not in ADMIN_IDS:
            print(f"🔍 DEBUG: Admin huquqi yo'q: {callback.from_user.id}")
            await callback.answer("❌ Sizda admin huquqlari yo'q!", show_alert=True)
            return
            
        print(f"🔍 DEBUG: Admin huquqi tasdiqlandi, FSM state o'rnatilmoqda")

        text = (
            "➕ **Admin qo'shish**\n\n"
            "🆔 **Admin ID kiriting:**\n"
            "Yangi admin bo'lishi kerak bo'lgan foydalanuvchining Telegram ID raqamini yuboring.\n\n"
            "💡 **Misol:** `123456789`\n\n"
            "❌ **Bekor qilish uchun:** /cancel"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin_management")]
        ])
        
        await state.set_state(AdminStates.waiting_for_admin_id)
        await callback.message.edit_text(text, reply_markup=keyboard)

    @dp.message(AdminStates.waiting_for_admin_id)
    async def add_admin_get_id(message: Message, state: FSMContext):
        print(f"🔍 DEBUG: Admin ID kiriting handler ishga tushdi. User: {message.from_user.id}, Text: {message.text}")
        
        if message.from_user.id not in ADMIN_IDS:
            print(f"🔍 DEBUG: Admin huquqi yo'q: {message.from_user.id}")
            await message.answer("❌ Sizda admin huquqlari yo'q!")
            return

        if message.text == "/cancel":
            await state.clear()
            await message.answer(
                "👑 **Admin Boshqaruvi**",
                reply_markup=get_admin_management_keyboard()
            )
            return

        try:
            admin_id = int(message.text.strip())
            print(f"🔍 DEBUG: Admin ID parse qilindi: {admin_id}")
        except ValueError:
            print(f"🔍 DEBUG: Noto'g'ri ID format: {message.text}")
            await message.answer("❌ **Xatolik!** Iltimos, to'g'ri ID raqam kiriting.\n\n💡 Misol: `123456789`")
            return

        # Adminni qo'shishga harakat qilish
        try:
            print(f"🔍 DEBUG: bot.get_chat({admin_id}) chaqirilmoqda...")
            # Foydalanuvchi ma'lumotlarini olish
            admin_user = await bot.get_chat(admin_id)
            username = admin_user.username
            first_name = admin_user.first_name
            print(f"🔍 DEBUG: Foydalanuvchi ma'lumotlari: {first_name}, @{username}")
            
            print(f"🔍 DEBUG: db.add_admin chaqirilmoqda...")
            success = await db.add_admin(
                user_id=admin_id,
                username=username,
                first_name=first_name,
                permissions='basic',
                added_by=message.from_user.id
            )
            print(f"🔍 DEBUG: db.add_admin natijasi: {success}")
            
            if success:
                    await message.answer(
                        f"✅ **Admin muvaffaqiyatli qo'shildi!**\n\n"
                        f"👤 **Foydalanuvchi:** {first_name}\n"
                        f"🆔 **ID:** `{admin_id}`\n"
                        f"📛 **Username:** @{username if username else 'Yoq'}\n"
                        f"🔐 **Huquq:** basic\n\n"
                        f"ℹ️ Admin endi botdan foydalana oladi.\n\n"
                        f"📋 Adminlar ro'yxatini ko'rish uchun: /admin_list"
                    )
                    # Optional: Send updated admin list
                    admins = await db.get_all_admins()
                    if admins:
                        text = f"📋 **Adminlar ro'yxati** ({len(admins)} ta)\n\n"
                        for i, admin in enumerate(admins, 1):
                            status = "✅ Faol" if admin.get('is_active', True) else "❌ Nofaol"
                            username = f"@{admin['username']}" if admin['username'] else "❌ Username yo'q"
                            name = admin['first_name'] or "❌ Nom yo'q"
                            permissions = admin['permissions'] or "basic"
                            text += f"{i}. **{name}** ({username})\n"
                            text += f"   🆔 ID: `{admin['user_id']}`\n"
                            text += f"   🔐 Huquq: {permissions}\n"
                            text += f"   📊 Holat: {status}\n"
                            text += f"   📅 Qo'shilgan: {admin.get('added_date', '')[:10]}\n\n"
                        await message.answer(text)
            else:
                print(f"🔍 DEBUG: Admin qo'shilmadi - allaqachon mavjud")
                await message.answer("❌ **Xatolik!** Bu foydalanuvchi allaqachon admin.")
                
        except Exception as e:
            print(f"🔍 DEBUG: Exception yuz berdi: {str(e)}")
            await message.answer(f"❌ **Xatolik!** Foydalanuvchi topilmadi yoki bot unga xabar yubora olmaydi.\n\nXatolik: {str(e)}")

        print(f"🔍 DEBUG: State tozalandi")
        await state.clear()

    @dp.callback_query(F.data == "remove_admin")
    async def remove_admin_handler(callback: CallbackQuery, state: FSMContext):
        if callback.from_user.id not in ADMIN_IDS:
            await callback.answer("❌ Sizda admin huquqlari yo'q!", show_alert=True)
            return

        # Adminlar ro'yxatini chiqarish
        admins = await db.get_all_admins()
        if not admins:
            await callback.message.edit_text("❌ O'chiradigan adminlar yo'q!", reply_markup=get_admin_management_keyboard())
            return
        text = "➖ **Admin o'chirish**\n\nO'chiradigan adminni tanlang:"
        keyboard = []
        SUPER_ADMIN_ID = 5425876649
        for admin in admins:
            if admin['user_id'] == SUPER_ADMIN_ID:
                keyboard.append([
                    InlineKeyboardButton(
                        text=f"👑 {admin['first_name'] or admin['user_id']} ({admin['user_id']}) - Ega",
                        callback_data="ignore_super_admin"
                    )
                ])
            else:
                keyboard.append([
                    InlineKeyboardButton(
                        text=f"🗑 {admin['first_name'] or admin['user_id']} ({admin['user_id']})",
                        callback_data=f"delete_admin_{admin['user_id']}"
                    )
                ])
        keyboard.append([InlineKeyboardButton(text="🔄 Yangilash", callback_data="remove_admin")])
        keyboard.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_management")])
        await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
        await state.clear()

    @dp.message(AdminStates.waiting_for_remove_admin_id)
    async def remove_admin_get_id(message: Message, state: FSMContext):
        if message.from_user.id not in ADMIN_IDS:
            await message.answer("❌ Sizda admin huquqlari yo'q!")
            return

        if message.text == "/cancel":
            await state.clear()
            await message.answer(
                "👑 **Admin Boshqaruvi**",
                reply_markup=get_admin_management_keyboard()
            )
            return

        # Bu handler endi kerak emas, o'chirish tugmasi orqali amalga oshiriladi
        await message.answer("❌ Bu amal tugma orqali amalga oshiriladi.")
        await state.clear()
    # Adminni tugma orqali o'chirish
    @dp.callback_query(F.data.startswith("delete_admin_"))
    async def delete_admin_callback(callback: CallbackQuery):
        if callback.from_user.id not in ADMIN_IDS:
            await callback.answer("❌ Sizda admin huquqlari yo'q!", show_alert=True)
            return
        SUPER_ADMIN_ID = 5425876649
        admin_id = int(callback.data.split("_")[-1])
        # O'zini o'chirishni taqiqlash yoki super adminni o'chirishni taqiqlash
        if admin_id == callback.from_user.id or admin_id == SUPER_ADMIN_ID:
            await callback.answer("❌ Ega adminni o'chirib bo'lmaydi!", show_alert=True)
            return
        success = await db.remove_admin(admin_id)
        if success:
            # O'chirgandan so'ng adminlar ro'yxatini yangilash
            admins = await db.get_all_admins()
            text = ""
            if not admins:
                text = "📋 **Adminlar ro'yxati**\n\n❌ Hech qanday admin topilmadi."
            else:
                text = f"📋 **Adminlar ro'yxati** ({len(admins)} ta)\n\n"
                for i, admin in enumerate(admins, 1):
                    status = "✅ Faol" if admin['is_active'] else "❌ Nofaol"
                    username = f"@{admin['username']}" if admin['username'] else "❌ Username yo'q"
                    name = admin['first_name'] or "❌ Nom yo'q"
                    permissions = admin['permissions'] or "basic"
                    extra = " - Ega" if admin['user_id'] == SUPER_ADMIN_ID else ""
                    text += f"{i}. **{name}** ({username}){extra}\n"
                    text += f"   🆔 ID: `{admin['user_id']}`\n"
                    text += f"   🔐 Huquq: {permissions}\n"
                    text += f"   📊 Holat: {status}\n"
                    text += f"   📅 Qo'shilgan: {admin['added_date'][:10]}\n\n"
            keyboard = [
                [InlineKeyboardButton(text="🔄 Yangilash", callback_data="admin_list")],
                [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_management")]
            ]
            await callback.message.edit_text(
                f"✅ **Admin muvaffaqiyatli o'chirildi!**\n\n"
                f"🆔 **ID:** `{admin_id}`\n"
                f"ℹ️ Foydalanuvchi endi oddiy foydalanuvchi hisoblanadi.\n\n"
                f"{text}",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
            )
        else:
            await callback.message.edit_text("❌ **Xatolik!** Bu ID da admin topilmadi.", reply_markup=get_admin_management_keyboard())
    
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