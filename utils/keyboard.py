from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


def get_admin_panel_keyboard() -> InlineKeyboardMarkup:
    """Admin panel klaviaturasi"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats"),
            InlineKeyboardButton(text="📺 Kanallar", callback_data="admin_channels")
        ],
        [
            InlineKeyboardButton(text="🎬 Kino boshqaruvi", callback_data="admin_movies"),
            InlineKeyboardButton(text="📢 Xabar yuborish", callback_data="admin_broadcast")
        ],
        [
            InlineKeyboardButton(text="💎 Premium obuna", callback_data="admin_premium")
        ],
        [
            InlineKeyboardButton(text="👑 Admin boshqaruvi", callback_data="admin_management")
        ]
    ])
    return keyboard


def get_channels_management_keyboard() -> InlineKeyboardMarkup:
    """Kanallar boshqaruvi klaviaturasi"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📋 Kanallar ro'yxati", callback_data="channels_list"),
            InlineKeyboardButton(text="➕ Kanal qo'shish", callback_data="add_channel")
        ],
        [
            InlineKeyboardButton(text="➖ Kanal o'chirish", callback_data="delete_channel"),
            InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_back")
        ]
    ])
    return keyboard


def get_movies_management_keyboard() -> InlineKeyboardMarkup:
    """Kinolar boshqaruvi klaviaturasi"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ Kino qo'shish", callback_data="add_movie"),
            InlineKeyboardButton(text="📋 Kinolar ro'yxati", callback_data="movies_list")
        ],
        [
            InlineKeyboardButton(text="🎬 4K qo'shish", callback_data="add_4k"),
            InlineKeyboardButton(text="🏆 Top kinolar", callback_data="top_movies")
        ],
        [
            InlineKeyboardButton(text="➖ Kino o'chirish", callback_data="delete_movie")
        ],
        [
            InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_back")
        ]
    ])
    return keyboard


def get_subscription_keyboard(channels: list, show_premium: bool = False) -> InlineKeyboardMarkup:
    """Majburiy obuna klaviaturasi"""
    keyboard = []
    
    # Har bir kanal uchun tugma
    for channel in channels:
        channel_name = channel['channel_name']
        channel_username = channel['channel_username']
        channel_url = f"https://t.me/{channel_username}" if channel_username else f"tg://resolve?domain={channel_username}"
        
        keyboard.append([
            InlineKeyboardButton(text=f"📢 {channel_name}", url=channel_url)
        ])
    
    # Premium tugmasi (agar yoqilgan bo'lsa)
    if show_premium:
        keyboard.append([
            InlineKeyboardButton(text="💎 Premium obuna", callback_data="show_premium")
        ])
    
    # Tekshirish tugmasi
    keyboard.append([
        InlineKeyboardButton(text="✅ Obunani tekshirish", callback_data="check_subscription")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_back_keyboard(callback_data: str = "admin_back") -> InlineKeyboardMarkup:
    """Orqaga tugmasi"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data=callback_data)]
    ])


def get_confirm_keyboard(confirm_data: str, cancel_data: str = "cancel") -> InlineKeyboardMarkup:
    """Tasdiqlash klaviaturasi"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Ha", callback_data=confirm_data),
            InlineKeyboardButton(text="❌ Yo'q", callback_data=cancel_data)
        ]
    ])


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Bekor qilish klaviaturasi"""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Bekor qilish")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def remove_keyboard() -> dict:
    """Klaviaturani olib tashlash"""
    return {"remove_keyboard": True}


def get_premium_management_keyboard(is_enabled: bool = False) -> InlineKeyboardMarkup:
    """Premium boshqaruvi klaviaturasi"""
    status_text = "🟢 Faol" if is_enabled else "🔴 Faol emas"
    toggle_text = "❌ O'chirish" if is_enabled else "✅ Yoqish"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💰 Narxlar sozlash", callback_data="premium_prices"),
            InlineKeyboardButton(text="📝 Tavsif o'zgartirish", callback_data="premium_description")
        ],
        [
            InlineKeyboardButton(text=f"{status_text}", callback_data="premium_status"),
            InlineKeyboardButton(text=toggle_text, callback_data="premium_toggle")
        ],
        [
            InlineKeyboardButton(text="📊 Premium statistika", callback_data="premium_stats"),
            InlineKeyboardButton(text="👥 Premium foydalanuvchilar", callback_data="premium_users")
        ],
        [
            InlineKeyboardButton(text="� Karta boshqaruvi", callback_data="manage_cards"),
            InlineKeyboardButton(text="🧾 To'lovlar", callback_data="pending_payments")
        ],
        [
            InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_back")
        ]
    ])
    return keyboard


def get_premium_subscription_keyboard(premium_settings: dict) -> InlineKeyboardMarkup:
    """Premium obuna klaviaturasi"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f"1️⃣ oy - {premium_settings['price_1month']:,} so'm", 
                callback_data="premium_pay_1m"
            )
        ],
        [
            InlineKeyboardButton(
                text=f"3️⃣ oy - {premium_settings['price_3months']:,} so'm", 
                callback_data="premium_pay_3m"
            )
        ],
        [
            InlineKeyboardButton(
                text=f"6️⃣ oy - {premium_settings['price_6months']:,} so'm", 
                callback_data="premium_pay_6m"
            )
        ],
        [
            InlineKeyboardButton(
                text=f"1️⃣2️⃣ oy - {premium_settings['price_12months']:,} so'm", 
                callback_data="premium_pay_12m"
            )
        ],
        [
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_premium")
        ]
    ])
    return keyboard


def get_payment_verification_keyboard(verification_id: int) -> InlineKeyboardMarkup:
    """To'lov tasdiqlash klaviaturasi"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"approve_payment_{verification_id}"),
            InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_payment_{verification_id}")
        ]
    ])
    return keyboard


def get_welcome_choice_keyboard() -> InlineKeyboardMarkup:
    """Boshlang'ich tanlov klaviaturasi (Premium vs Bepul)"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💎 Premium obuna", callback_data="choose_premium")
        ],
        [
            InlineKeyboardButton(text="🆓 Bepul ko'rish", callback_data="choose_free")
        ],
        [
            InlineKeyboardButton(text="💳 To'lovlarim", callback_data="my_payments")
        ]
    ])
    return keyboard

def get_user_payments_keyboard() -> InlineKeyboardMarkup:
    """Foydalanuvchi to'lovlari klaviaturasi"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔄 Yangilash", callback_data="my_payments")
        ],
        [
            InlineKeyboardButton(text="🔙 Orqaga", callback_data="user_back_to_menu")
        ]
    ])
    return keyboard


def get_card_management_keyboard() -> InlineKeyboardMarkup:
    """Karta boshqaruvi klaviaturasi"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ Karta qo'shish", callback_data="add_card"),
            InlineKeyboardButton(text="🔄 Karta almashtirish", callback_data="replace_card")
        ],
        [
            InlineKeyboardButton(text="📋 Kartalar ro'yxati", callback_data="list_cards")
        ],
        [
            InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_premium")
        ]
    ])
    return keyboard


def get_admin_management_keyboard() -> InlineKeyboardMarkup:
    """Admin boshqaruvi klaviaturasi"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📋 Adminlar ro'yxati", callback_data="admin_list"),
            InlineKeyboardButton(text="➕ Admin qo'shish", callback_data="add_admin")
        ],
        [
            InlineKeyboardButton(text="➖ Admin o'chirish", callback_data="remove_admin"),
            InlineKeyboardButton(text="⚙️ Huquqlar", callback_data="admin_permissions")
        ],
        [
            InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_back")
        ]
    ])
    return keyboard


def get_admin_permissions_keyboard() -> InlineKeyboardMarkup:
    """Admin huquqlari klaviaturasi"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔰 Asosiy", callback_data="perm_basic"),
            InlineKeyboardButton(text="📊 Statistika", callback_data="perm_stats")
        ],
        [
            InlineKeyboardButton(text="🎬 Kinolar", callback_data="perm_movies"),
            InlineKeyboardButton(text="📺 Kanallar", callback_data="perm_channels")
        ],
        [
            InlineKeyboardButton(text="📢 Xabar yuborish", callback_data="perm_broadcast"),
            InlineKeyboardButton(text="💎 Premium", callback_data="perm_premium")
        ],
        [
            InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_management")
        ]
    ])
    return keyboard


def get_admin_actions_keyboard(admin_id: int) -> InlineKeyboardMarkup:
    """Admin harakatlari klaviaturasi"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⚙️ Huquqlarni o'zgartirish", callback_data=f"edit_admin_{admin_id}"),
            InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"delete_admin_{admin_id}")
        ],
        [
            InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_list")
        ]
    ])
    return keyboard