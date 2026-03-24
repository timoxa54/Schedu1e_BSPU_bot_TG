import telebot
from datetime import date, timedelta
from config import TOKEN, GROUP_ID
from telebot import types
from notifications import start_scheduler, register_user

from schedule import (
    get_week_schedule,
    get_next_week_schedule,
    format_day,
    group_by_date
)

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

WEEKDAYS = {
    "Monday": "📅 Понедельник",
    "Tuesday": "📅 Вторник",
    "Wednesday": "📅 Среда",
    "Thursday": "📅 Четверг",
    "Friday": "📅 Пятница",
    "Saturday": "📅 Суббота",
    "Sunday": "📅 Воскресенье",
}


# 🔘 КЛАВИАТУРА
def main_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)

    kb.add(
        types.KeyboardButton("📅 Сегодня"),
        types.KeyboardButton("📆 Завтра")
    )
    kb.add(
        types.KeyboardButton("🗓 Неделя"),
        types.KeyboardButton("⏭ Следующая неделя")
    )

    return kb


# 🚀 START
@bot.message_handler(commands=["start"])
def start(message):
    register_user(message.chat.id)

    bot.send_message(
        message.chat.id,
        "Привет 👋\n\nВыбери действие 👇",
        reply_markup=main_keyboard()
    )


# 📅 СЕГОДНЯ
@bot.message_handler(commands=["today"])
def today(message):
    lessons = get_week_schedule(GROUP_ID)
    today_iso = date.today().isoformat()

    today_lessons = [
        l for l in lessons if l["дата"].startswith(today_iso)
    ]

    if not today_lessons:
        bot.send_message(message.chat.id, "🎉 Сегодня занятий нет", reply_markup=main_keyboard())
        return

    header = f"<b>📅 Сегодня — {date.today().strftime('%d.%m.%Y')}</b>\n\n"
    bot.send_message(message.chat.id, header + format_day(today_lessons), reply_markup=main_keyboard())


# 📅 ЗАВТРА
@bot.message_handler(commands=["tomorrow"])
def tomorrow(message):
    lessons = get_week_schedule(GROUP_ID)
    tomorrow_date = date.today() + timedelta(days=1)
    tomorrow_iso = tomorrow_date.isoformat()

    tomorrow_lessons = [
        l for l in lessons if l["дата"].startswith(tomorrow_iso)
    ]

    if not tomorrow_lessons:
        bot.send_message(message.chat.id, "🎉 Завтра занятий нет", reply_markup=main_keyboard())
        return

    header = f"<b>📅 Завтра — {tomorrow_date.strftime('%d.%m.%Y')}</b>\n\n"
    bot.send_message(message.chat.id, header + format_day(tomorrow_lessons), reply_markup=main_keyboard())


# 📅 НЕДЕЛЯ
@bot.message_handler(commands=["week"])
def week(message):
    lessons = get_week_schedule(GROUP_ID)
    days = group_by_date(lessons)

    text = "<b>📅 Текущая неделя</b>\n"

    for day in sorted(days):
        date_obj = date.fromisoformat(day)
        weekday = WEEKDAYS[date_obj.strftime('%A')]

        text += f"\n<b>{weekday} {date_obj.strftime('%d.%m')}</b>\n\n"
        text += format_day(days[day])

    bot.send_message(message.chat.id, text, reply_markup=main_keyboard())


# 📅 СЛЕДУЮЩАЯ НЕДЕЛЯ
@bot.message_handler(commands=["nextweek"])
def next_week(message):
    lessons = get_next_week_schedule(GROUP_ID)
    days = group_by_date(lessons)

    text = "<b>📅 Следующая неделя</b>\n"

    for day in sorted(days):
        date_obj = date.fromisoformat(day)
        weekday = WEEKDAYS[date_obj.strftime('%A')]

        text += f"\n<b>{weekday} {date_obj.strftime('%d.%m')}</b>\n\n"
        text += format_day(days[day])

    bot.send_message(message.chat.id, text, reply_markup=main_keyboard())


# 🔘 ОБРАБОТКА КНОПОК (ВСЕГДА ВНИЗУ!)
@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    text = message.text

    if text == "📅 Сегодня":
        today(message)

    elif text == "📆 Завтра":
        tomorrow(message)

    elif text == "🗓 Неделя":
        week(message)

    elif text == "⏭ Следующая неделя":
        next_week(message)

    else:
        bot.send_message(message.chat.id, "Используй кнопки 👇", reply_markup=main_keyboard())


print("🤖 Бот запущен")

# 🔔 запускаем уведомления
start_scheduler(bot)

# 🚀 запуск бота
bot.infinity_polling()