import requests
from collections import defaultdict
from datetime import date, timedelta

TYPE_MAP = {
    "лек": "📖 Лекция",
    "пр.": "🧪 Практика",
    "лаб.": "🔬 Лабораторная"
}


def parse_discipline(text: str):
    parts = text.split(" ", 1)
    if parts[0] in TYPE_MAP:
        return TYPE_MAP[parts[0]], parts[1]
    return "📘 Занятие", text


def get_week_schedule(group_id: int, start_date: str | None = None):
    if start_date is None:
        start_date = date.today().isoformat()

    url = "https://asu.bspu.ru/api/Rasp"
    params = {
        "idGroup": group_id,
        "sdate": start_date
    }

    r = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    return r.json()["data"]["rasp"]


def get_next_week_schedule(group_id: int):
    next_week = date.today() + timedelta(days=7)
    return get_week_schedule(group_id, start_date=next_week.isoformat())


def format_day(lessons: list) -> str:
    text = ""

    for l in sorted(lessons, key=lambda x: x["датаНачала"]):
        time = f"{l['начало']}–{l['конец']}"
        room = l["аудитория"]

        subject_type, subject_name = parse_discipline(l["дисциплина"])
        teacher = l["преподаватель"]

        text += (
            f"⏰ <b>{time}</b>  |  <b>{room}</b>\n"
            f"{subject_type} — {subject_name}\n"
            f"👨‍🏫 {teacher}\n\n"
        )

    return text


def group_by_date(lessons: list):
    days = defaultdict(list)

    for l in lessons:
        days[l["дата"][:10]].append(l)

    return days