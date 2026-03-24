from apscheduler.schedulers.background import BackgroundScheduler
from datetime import date, timedelta
import pytz

from schedule import get_week_schedule, format_day

USERS = set()


def register_user(chat_id):
    USERS.add(chat_id)


def send_tomorrow(bot):
    lessons = get_week_schedule(25289)

    tomorrow = date.today() + timedelta(days=1)
    tomorrow_iso = tomorrow.isoformat()

    tomorrow_lessons = [
        l for l in lessons if l["дата"].startswith(tomorrow_iso)
    ]

    for chat_id in USERS:
        if not tomorrow_lessons:
            bot.send_message(chat_id, "🎉 Завтра занятий нет")
        else:
            text = (
                f"<b>📅 Завтра — {tomorrow.strftime('%d.%m.%Y')}</b>\n\n"
                + format_day(tomorrow_lessons)
            )
            bot.send_message(chat_id, text)


def start_scheduler(bot):
    scheduler = BackgroundScheduler(timezone=pytz.timezone("Asia/Yekaterinburg"))

    scheduler.add_job(lambda: send_tomorrow(bot), "cron", hour=19, minute=0)
    scheduler.add_job(lambda: send_tomorrow(bot), "cron", hour=23, minute=0)

    scheduler.start()