"""Telegram weather bot powered by Open-Meteo and requests."""

from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime
from typing import Any

import requests
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
REQUEST_TIMEOUT = 12

WEATHER_CODES = {
    0: "صاف",
    1: "عمدتاً صاف",
    2: "نیمه‌ابری",
    3: "ابری",
    45: "مه‌آلود",
    48: "مه یخ‌زننده",
    51: "نم‌نم باران خفیف",
    53: "نم‌نم باران متوسط",
    55: "نم‌نم باران شدید",
    56: "نم‌نم باران یخ‌زننده خفیف",
    57: "نم‌نم باران یخ‌زننده شدید",
    61: "باران خفیف",
    63: "باران متوسط",
    65: "باران شدید",
    66: "باران یخ‌زننده خفیف",
    67: "باران یخ‌زننده شدید",
    71: "برف خفیف",
    73: "برف متوسط",
    75: "برف شدید",
    77: "دانه‌های برف",
    80: "رگبار خفیف",
    81: "رگبار متوسط",
    82: "رگبار شدید",
    85: "رگبار برف خفیف",
    86: "رگبار برف شدید",
    95: "رعدوبرق",
    96: "رعدوبرق همراه تگرگ خفیف",
    99: "رعدوبرق همراه تگرگ شدید",
}

WEATHER_CODES_EN = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog", 51: "Light drizzle",
    53: "Moderate drizzle", 55: "Dense drizzle", 56: "Light freezing drizzle",
    57: "Dense freezing drizzle", 61: "Slight rain", 63: "Moderate rain",
    65: "Heavy rain", 66: "Light freezing rain", 67: "Heavy freezing rain",
    71: "Slight snowfall", 73: "Moderate snowfall", 75: "Heavy snowfall",
    77: "Snow grains", 80: "Slight rain showers", 81: "Moderate rain showers",
    82: "Violent rain showers", 85: "Slight snow showers", 86: "Heavy snow showers",
    95: "Thunderstorm", 96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}

WIND_DIRECTIONS = ("شمال", "شمال‌شرق", "شرق", "جنوب‌شرق", "جنوب", "جنوب‌غرب", "غرب", "شمال‌غرب")
WIND_DIRECTIONS_EN = ("north", "northeast", "east", "southeast", "south", "southwest", "west", "northwest")


class WeatherError(Exception):
    """An expected error that can safely be shown to the user."""


def wind_direction(degrees: float | None, language: str = "fa") -> str:
    if degrees is None:
        return "نامشخص" if language == "fa" else "unknown"
    directions = WIND_DIRECTIONS if language == "fa" else WIND_DIRECTIONS_EN
    return directions[round(degrees / 45) % 8]


def short_time(value: str | None, unknown: str = "نامشخص") -> str:
    if not value:
        return unknown
    try:
        return datetime.fromisoformat(value).strftime("%H:%M")
    except ValueError:
        return value


def api_get(url: str, params: dict[str, Any]) -> dict[str, Any]:
    try:
        response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as exc:
        raise WeatherError("ارتباط با سرویس هواشناسی برقرار نشد. کمی بعد دوباره تلاش کنید.") from exc


def find_city(city: str) -> dict[str, Any]:
    data = api_get(
        GEOCODING_URL,
        {"name": city, "count": 1, "language": "en", "format": "json"},
    )
    results = data.get("results") or []
    if not results:
        raise WeatherError("شهر پیدا نشد. نام شهر را به انگلیسی و دقیق‌تر بفرستید؛ مثلاً: Tehran")
    return results[0]


def get_forecast(location: dict[str, Any]) -> dict[str, Any]:
    return api_get(
        FORECAST_URL,
        {
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "timezone": "auto",
            "forecast_days": 5,
            "current": ",".join(
                [
                    "temperature_2m", "apparent_temperature", "relative_humidity_2m",
                    "precipitation", "rain", "showers", "snowfall", "weather_code",
                    "cloud_cover", "surface_pressure", "wind_speed_10m",
                    "wind_direction_10m", "wind_gusts_10m", "is_day",
                ]
            ),
            "daily": ",".join(
                [
                    "weather_code", "temperature_2m_max", "temperature_2m_min",
                    "apparent_temperature_max", "apparent_temperature_min",
                    "sunrise", "sunset", "precipitation_sum",
                    "precipitation_probability_max", "wind_speed_10m_max",
                ]
            ),
        },
    )


def value(data: dict[str, Any], key: str, suffix: str = "", unknown: str = "نامشخص") -> str:
    item = data.get(key)
    return f"{item}{suffix}" if item is not None else unknown


def format_weather(location: dict[str, Any], forecast: dict[str, Any], language: str = "fa") -> str:
    current = forecast.get("current", {})
    daily = forecast.get("daily", {})
    units = forecast.get("current_units", {})
    place = ", ".join(filter(None, [location.get("name"), location.get("admin1"), location.get("country")]))
    code = current.get("weather_code")
    if language == "en":
        unknown = "unknown"
        day_state = "day" if current.get("is_day") == 1 else "night"
        lines = [
            f"🌍 Weather for {place}",
            f"🕒 Local time: {current.get('time', unknown)} ({forecast.get('timezone_abbreviation', '')})",
            f"🌤 Conditions: {WEATHER_CODES_EN.get(code, unknown)} — {day_state}", "",
            "📍 Current conditions",
            f"🌡 Temperature: {value(current, 'temperature_2m', units.get('temperature_2m', '°C'), unknown)}",
            f"🤒 Feels like: {value(current, 'apparent_temperature', units.get('apparent_temperature', '°C'), unknown)}",
            f"💧 Humidity: {value(current, 'relative_humidity_2m', '%', unknown)}",
            f"☁️ Cloud cover: {value(current, 'cloud_cover', '%', unknown)}",
            f"🌧 Current precipitation: {value(current, 'precipitation', ' mm', unknown)}",
            f"🌬 Wind: {value(current, 'wind_speed_10m', ' km/h', unknown)} from {wind_direction(current.get('wind_direction_10m'), 'en')}",
            f"💨 Gusts: {value(current, 'wind_gusts_10m', ' km/h', unknown)}",
            f"🔵 Surface pressure: {value(current, 'surface_pressure', ' hPa', unknown)}",
        ]
    else:
        unknown = "نامشخص"
        day_state = "روز" if current.get("is_day") == 1 else "شب"
        lines = [
            f"🌍 هواشناسی {place}",
            f"🕒 زمان محلی: {current.get('time', unknown)} ({forecast.get('timezone_abbreviation', '')})",
            f"🌤 وضعیت: {WEATHER_CODES.get(code, unknown)} — {day_state}", "",
            "📍 وضعیت فعلی",
            f"🌡 دما: {value(current, 'temperature_2m', units.get('temperature_2m', '°C'))}",
            f"🤒 دمای احساسی: {value(current, 'apparent_temperature', units.get('apparent_temperature', '°C'))}",
            f"💧 رطوبت: {value(current, 'relative_humidity_2m', '%')}",
            f"☁️ پوشش ابر: {value(current, 'cloud_cover', '%')}",
            f"🌧 بارش فعلی: {value(current, 'precipitation', ' mm')}",
            f"🌬 باد: {value(current, 'wind_speed_10m', ' km/h')} از {wind_direction(current.get('wind_direction_10m'))}",
            f"💨 تندباد: {value(current, 'wind_gusts_10m', ' km/h')}",
            f"🔵 فشار سطح زمین: {value(current, 'surface_pressure', ' hPa')}",
        ]

    dates = daily.get("time", [])
    if dates:
        if language == "en":
            lines.extend(["", f"🌅 Sunrise today: {short_time(daily.get('sunrise', [None])[0], unknown)}",
                          f"🌇 Sunset today: {short_time(daily.get('sunset', [None])[0], unknown)}", "", "📅 5-day forecast"])
        else:
            lines.extend(["", f"🌅 طلوع امروز: {short_time(daily.get('sunrise', [None])[0])}",
                          f"🌇 غروب امروز: {short_time(daily.get('sunset', [None])[0])}", "", "📅 پیش‌بینی ۵ روزه"])
        for i, date in enumerate(dates[:5]):
            try:
                label = datetime.fromisoformat(date).strftime("%Y-%m-%d")
                descriptions = WEATHER_CODES if language == "fa" else WEATHER_CODES_EN
                desc = descriptions.get(daily["weather_code"][i], unknown)
                low, high = daily["temperature_2m_min"][i], daily["temperature_2m_max"][i]
                chance = daily["precipitation_probability_max"][i]
                rain = daily["precipitation_sum"][i]
                wind = daily["wind_speed_10m_max"][i]
                if language == "en":
                    lines.append(f"• {label}: {desc} | {low} to {high}°C | rain chance {chance}% ({rain} mm) | wind {wind} km/h")
                else:
                    lines.append(f"• {label}: {desc} | {low} تا {high}°C | احتمال بارش {chance}% ({rain} mm) | باد {wind} km/h")
            except (KeyError, IndexError, TypeError):
                continue

    lines.extend(["", "منبع داده: Open-Meteo.com" if language == "fa" else "Data source: Open-Meteo.com"])
    return "\n".join(lines)


def fetch_weather(city: str, language: str = "fa") -> str:
    location = find_city(city)
    return format_weather(location, get_forecast(location), language)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text(
            "سلام! زبان را انتخاب کنید.\nHello! Please choose your language.",
            reply_markup=language_keyboard(),
        )


def language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("🇮🇷 فارسی", callback_data="lang_fa"),
          InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")]]
    )


async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if update.message:
        await update.message.reply_text("زبان / Language:", reply_markup=language_keyboard())


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    if context.user_data.get("language", "fa") == "en":
        text = (
            "🤖 Weather Bot Help\n\n"
            "Send an English city name to receive current weather and a five-day forecast.\n\n"
            "How to use:\n1. Send Tehran, London, or New York.\n"
            "2. Wait a few seconds.\n3. For similar names, add the country: Cambridge, UK.\n\n"
            "Commands:\n/start — Start and choose language\n/help — Show help\n"
            "/language — Change language\n/weather CITY — Example: /weather Istanbul\n\n"
            "Reports include temperature, feels-like, humidity, clouds, precipitation, "
            "pressure, wind, gusts, sunrise, sunset, and a five-day forecast."
        )
    else:
        text = (
            "🤖 راهنمای بات هواشناسی\n\n"
            "نام شهر را انگلیسی بفرستید تا وضعیت فعلی و پیش‌بینی پنج‌روزه را دریافت کنید.\n\n"
            "روش استفاده:\n۱. Tehran، London یا New York را ارسال کنید.\n"
            "۲. چند ثانیه منتظر بمانید.\n۳. برای شهر هم‌نام، کشور را اضافه کنید: Cambridge, UK.\n\n"
            "فرمان‌ها:\n/start — شروع و انتخاب زبان\n/help — نمایش راهنما\n"
            "/language — تغییر زبان\n/weather CITY — مثال: /weather Istanbul\n\n"
            "گزارش شامل دما، دمای احساسی، رطوبت، ابر، بارش، فشار، باد، تندباد، "
            "طلوع، غروب و پیش‌بینی پنج‌روزه است."
        )
    await update.message.reply_text(text)


async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query:
        return
    await query.answer()
    language = "en" if query.data == "lang_en" else "fa"
    context.user_data["language"] = language
    if language == "en":
        text = "✅ Language set to English.\nSend a city name in English. Example: London or New York"
    else:
        text = "✅ زبان روی فارسی تنظیم شد.\nنام شهر را به انگلیسی بفرستید. مثال: Tehran یا Istanbul"
    await query.edit_message_text(text)


async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    city = " ".join(context.args).strip()
    language = context.user_data.get("language", "fa")
    if not city:
        message = ("بعد از دستور نام شهر را انگلیسی بنویسید؛ مثال: /weather London"
                   if language == "fa" else "Enter an English city name after the command. Example: /weather London")
        await update.message.reply_text(message)
        return
    await send_weather(update, city, language)


async def city_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message and update.message.text:
        await send_weather(update, update.message.text.strip(), context.user_data.get("language", "fa"))


async def send_weather(update: Update, city: str, language: str) -> None:
    if not update.message:
        return
    loading = "⏳ در حال دریافت اطلاعات هواشناسی…" if language == "fa" else "⏳ Fetching weather data…"
    status = await update.message.reply_text(loading)
    try:
        report = await asyncio.to_thread(fetch_weather, city, language)
        await status.edit_text(report)
    except WeatherError:
        message = ("❌ شهر پیدا نشد یا ارتباط با سرویس هواشناسی برقرار نشد. نام انگلیسی شهر را بررسی کنید."
                   if language == "fa" else
                   "❌ The city was not found or the weather service is unavailable. Check the English city name.")
        await status.edit_text(message)
    except Exception:
        logging.exception("Unexpected error while processing city %r", city)
        message = ("❌ خطای غیرمنتظره‌ای رخ داد. لطفاً دوباره تلاش کنید."
                   if language == "fa" else "❌ An unexpected error occurred. Please try again.")
        await status.edit_text(message)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.error("Telegram update failed: %s", update, exc_info=context.error)


def main() -> None:
    logging.basicConfig(format="%(asctime)s | %(levelname)s | %(name)s | %(message)s", level=logging.INFO)
    load_dotenv()
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN is missing. Copy .env.example to .env and put your BotFather token in it. "
            "| توکن تنظیم نشده؛ فایل .env.example را به .env کپی و توکن BotFather را داخل آن قرار دهید."
        )

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("language", language_command))
    app.add_handler(CallbackQueryHandler(choose_language, pattern=r"^lang_(fa|en)$"))
    app.add_handler(CommandHandler("weather", weather_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, city_message))
    app.add_error_handler(error_handler)
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
