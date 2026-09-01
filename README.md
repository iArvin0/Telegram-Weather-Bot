# ربات هواشناسی تلگرام | Telegram Weather Bot

## فارسی

این پروژه یک ربات دو‌زبانهٔ تلگرام است. نام شهر را به انگلیسی دریافت می‌کند و با سرویس Open-Meteo گزارش کامل هواشناسی را به فارسی یا انگلیسی نمایش می‌دهد. Open-Meteo به API Key جداگانه نیاز ندارد.

### امکانات

- رابط فارسی و انگلیسی با دکمهٔ انتخاب زبان
- جست‌وجوی شهرهای سراسر جهان
- دما، دمای احساسی، رطوبت، پوشش ابر و فشار
- بارش، سرعت و جهت باد و تندباد
- وضعیت روز/شب، طلوع و غروب
- پیش‌بینی پنج‌روزه، احتمال بارش و کمینه/بیشینه دما
- مدیریت شهر نامعتبر، قطعی اینترنت و خطاهای سرویس

### همهٔ فرمان‌ها

| فرمان | توضیح |
|---|---|
| `/start` | شروع بات و نمایش انتخاب زبان |
| `/help` | نمایش راهنما، روش کار، امکانات و فرمان‌ها |
| `/language` | تغییر زبان فارسی یا انگلیسی |
| `/weather CITY` | دریافت هوا؛ مثال: `/weather Tehran` |

نام شهر را می‌توان مستقیماً نیز فرستاد و استفاده از `/weather` اجباری نیست.

### روش کار با بات

1. در تلگرام `/start` را بفرستید.
2. «فارسی» یا `English` را انتخاب کنید.
3. نام شهر را انگلیسی ارسال کنید؛ مانند `Tehran`، `Istanbul` یا `New York`.
4. برای شهرهای هم‌نام، کشور را اضافه کنید؛ مانند `Cambridge, UK`.
5. با `/help` راهنمای کامل داخل بات نمایش داده می‌شود.

### پیش‌نیازها

- Python 3.10 یا جدیدتر
- اینترنت
- توکن ربات از `@BotFather`

### دریافت توکن

در تلگرام وارد `@BotFather` شوید، `/newbot` را ارسال و مراحل را انجام دهید. توکن را محرمانه نگه دارید و در GitHub یا پیام عمومی منتشر نکنید.

### نصب در Windows PowerShell

```powershell
cd C:\path\to\telegram-weather-bot
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
py bot.py
```

فایل `.env` باید حاوی توکن واقعی باشد:

```env
TELEGRAM_BOT_TOKEN=123456789:YOUR_REAL_BOTFATHER_TOKEN
```

اگر PowerShell فعال‌سازی محیط را مسدود کرد:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### نصب در Linux/macOS

```bash
cd /path/to/telegram-weather-bot
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
nano .env
python bot.py
```

### رفع خطاهای رایج

- `TELEGRAM_BOT_TOKEN is missing`: فایل `.env` یا توکن آن تنظیم نشده است.
- `No module named ...`: محیط مجازی را فعال و requirements را نصب کنید.
- شهر پیدا نمی‌شود: نام انگلیسی و کشور را وارد کنید؛ مانند `Paris, France`.
- بات پاسخ نمی‌دهد: اینترنت، اعتبار توکن و باز بودن `bot.py` را بررسی کنید.

---

## English

This is a bilingual Telegram bot. It accepts an English city name and uses Open-Meteo to return a detailed weather report in Persian or English. Open-Meteo does not require a separate API key.

### Features

- Persian and English interface with language buttons
- Worldwide city search
- Temperature, apparent temperature, humidity, cloud cover, and pressure
- Precipitation, wind speed/direction, and gusts
- Day/night status, sunrise, and sunset
- Five-day forecast, precipitation probability, and minimum/maximum temperatures
- Friendly handling of invalid cities, network errors, and service failures

### All commands

| Command | Description |
|---|---|
| `/start` | Start the bot and display language selection |
| `/help` | Show help, usage, features, and commands |
| `/language` | Switch between Persian and English |
| `/weather CITY` | Get city weather; example: `/weather London` |

You can also send a city name directly; `/weather` is optional.

### Using the bot

1. Send `/start` in Telegram.
2. Select `فارسی` or `English`.
3. Send an English city name such as `Tehran`, `Istanbul`, or `New York`.
4. For similarly named cities, include the country, such as `Cambridge, UK`.
5. Send `/help` at any time for complete in-chat instructions.

### Requirements

- Python 3.10 or newer
- Internet access
- A Telegram bot token from `@BotFather`

### Getting a token

Open `@BotFather` in Telegram, send `/newbot`, and follow the prompts. Keep the token secret; never commit it to GitHub or post it publicly.

### Windows PowerShell installation

```powershell
cd C:\path\to\telegram-weather-bot
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
py bot.py
```

The `.env` file must contain the real token:

```env
TELEGRAM_BOT_TOKEN=123456789:YOUR_REAL_BOTFATHER_TOKEN
```

If PowerShell blocks environment activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### Linux/macOS installation

```bash
cd /path/to/telegram-weather-bot
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
nano .env
python bot.py
```

### Troubleshooting

- `TELEGRAM_BOT_TOKEN is missing`: create `.env` and add a valid token.
- `No module named ...`: activate the virtual environment and install requirements.
- City not found: use an English name with the country, for example `Paris, France`.
- No bot response: check the internet, token, and whether `bot.py` is running.

### Data and privacy

Submitted city names are sent to [Open-Meteo](https://open-meteo.com/) for geocoding and weather data. The Telegram token is loaded locally from `.env`, which is excluded by `.gitignore`.
