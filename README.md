# Kinobot - Telegram Movie Bot

Telegram orqali kino yuboruvchi bot. Bot foydalanuvchilarga kino kodlari orqali kinolar yuboradi va majburiy obuna tizimi bilan ishlaydi.

## ✨ Xususiyatlari

- **🎬 Kino Yuborish**: Foydalanuvchilar kino kodlari orqali kinolar olishlari mumkin
- **📢 Majburiy Obuna**: Botdan foydalanish uchun majburiy kanallar
- **👑 Admin Panel**: Statistika, kino boshqaruvi, kanal boshqaruvi
- **📊 Statistika**: Foydalanuvchilar, kinolar, kanallar haqida ma'lumot
- **📩 Ommaviy Xabar**: Barcha foydalanuvchilarga xabar yuborish
- **🏆 Top Kinolar**: Eng ko'p ko'rilgan kinolar ro'yxati
- **🔄 Avtomatik Baza**: Kinolar avtomatik baza kanalga yuboriladi

## 📋 Talablar

- Python 3.8+
- aiogram 3.3.0+
- aiosqlite
- Telegram Bot Token
- Admin ID

## 🚀 O'rnatish

### 1. Repository ni klonlash
```bash
git clone <repository-url>
cd kinobot
```

### 2. Virtual muhit yaratish
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

### 3. Kerakli kutubxonalarni o'rnatish
```bash
pip install -r requirements.txt
```

### 4. Konfiguratsiya
`config.py` faylida quyidagi sozlamalarni o'rnating:
- `BOT_TOKEN`: Telegram bot tokeni (@BotFather dan olingan)
- `ADMIN_IDS`: Admin ID lari ro'yxati
- `BASE_CHANNEL_ID`: Baza kanal ID si (kinolar saqlanadigan kanal)

### 5. Botni ishga tushirish
```bash
python bot.py
```
yoki VS Code da `Ctrl+Shift+P` > "Tasks: Run Task" > "Run Kinobot"

## ⚙️ Konfiguratsiya

### config.py da o'zgartirishlar kerak:
```python
# Bot tokeni - @BotFather dan oling
BOT_TOKEN = "sizning_bot_tokeningiz"

# Admin ID lari - Telegram ID lar
ADMIN_IDS = [123456789, 987654321]  # sizning ID laringiz

# Baza kanal ID si - kinolar saqlanadigan kanal
BASE_CHANNEL_ID = -1001234567890  # haqiqiy kanal ID
```

### Kanal ID sini qanday topish:
1. Kanalga botni admin qilib qo'shing
2. Kanalga xabar yuboring
3. `https://api.telegram.org/bot<BOT_TOKEN>/getUpdates` ga kirib ID ni ko'ring

## 👑 Admin Komandalar

### `/admin` - Admin Panel
- **📊 Statistika**: 
  - Jami foydalanuvchilar
  - Bugungi/7 kunlik yangi foydalanuvchilar
  - Faol foydalanuvchilar
  - Kinolar va ko'rishlar soni
  - Kanallar va broadcast statistikasi

- **📺 Kanallar Boshqaruvi**:
  - Majburiy obuna kanallar ro'yxati
  - Kanal qo'shish (ID va nom bilan)
  - Kanal o'chirish

- **🎬 Kinolar Boshqaruvi**:
  - Kino qo'shish (kod + nom + video)
  - Kinolar ro'yxati
  - Kino o'chirish
  - Top 10 eng ko'p ko'rilgan kinolar

- **📢 Xabar Yuborish**:
  - Barcha foydalanuvchilarga xabar
  - Matn, rasm yoki video yuborish mumkin
  - Yuborish statistikasi

## 👥 Foydalanuvchilar uchun

1. **Boshlash**: `/start` komandasi
2. **Obuna**: Majburiy kanallarga obuna bo'lish
3. **Kino So'rash**: Kino kodini yuborish (masalan: `001`)
4. **Kino Olish**: Bot kino mavjud bo'lsa yuboradi

## 📁 Loyiha Strukturasi

```
kinobot/
├── .venv/                    # Virtual muhit
├── .vscode/                  # VS Code sozlamalar
├── .github/
│   └── copilot-instructions.md
├── bot.py                    # Asosiy bot fayli
├── config.py                 # Konfiguratsiya
├── database.py               # Ma'lumotlar bazasi (SQLite)
├── kinobot.db               # Baza fayli (avtomatik yaratiladi)
├── handlers/                 # Bot handlerlari
│   ├── __init__.py
│   ├── admin.py             # Admin funksiyalari
│   ├── user.py              # Foydalanuvchi funksiyalari
│   └── callback.py          # Callback handleri
├── utils/                    # Yordamchi funksiyalar
│   ├── __init__.py
│   ├── keyboard.py          # Inline klaviaturalar
│   └── helpers.py           # Yordamchi funksiyalar
├── requirements.txt          # Python kutubxonalar
└── README.md                # Bu fayl
```

## 🔧 Xususiy Sozlamalar

### Xabar matnlarini o'zgartirish:
`config.py` da quyidagi o'zgaruvchilarni o'zgartiring:
- `WELCOME_TEXT` - Xush kelibsiz xabari
- `SUBSCRIBED_TEXT` - Obuna tasdiqlangan xabar
- `NOT_SUBSCRIBED_TEXT` - Obuna bo'lmagan xabar
- `MOVIE_NOT_FOUND_TEXT` - Kino topilmagan xabar

### Ma'lumotlar bazasi joylashuvi:
```python
DATABASE_PATH = "kinobot.db"  # fayl nomi
```

## 🐛 Muammolarni hal qilish

### Bot ishlamasa:
1. Bot tokeni to'g'riligini tekshiring
2. Internet aloqasini tekshiring
3. Loglarni ko'rib chiqing

### Kino yuborilmasa:
1. Bot baza kanaliga admin ekanligini tekshiring
2. Kanal ID to'g'riligini tekshiring
3. Video fayl yaroqli ekanligini tekshiring

### Obuna ishlamasa:
1. Bot kanallarda admin ekanligini tekshiring
2. Kanal ID lari to'g'riligini tekshiring

## 📊 Database Schema

- **users**: Foydalanuvchilar ma'lumoti
- **movies**: Kinolar (kod, nom, file_id, ko'rishlar)
- **channels**: Majburiy obuna kanallari
- **movie_views**: Kino ko'rishlar tarixi
- **broadcast_stats**: Xabar yuborish statistikasi

## 🚀 Ishga Tushirish

1. Barcha sozlamalarni to'g'ri qiling
2. Botni ishga tushiring: `python bot.py`
3. Telegram da botni toping va `/start` bosing
4. Admin panelga kirish: `/admin`

## 📞 Qo'llab-quvvatlash

Muammolar yoki savollar bo'lsa, admin bilan bog'laning yoki GitHub Issues da xabar qoldiring.