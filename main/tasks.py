from datetime import timedelta, datetime
from celery import shared_task
from timezone_field.backends import pytz

from config import settings
from main.models import Habit
from main.services import send_tg_message


@shared_task()
def tg_notification():
    zone = pytz.timezone(settings.CELERY_TIMEZONE)
    now = datetime.now(zone)

    habits = Habit.objects.all()
    print(f"Найдено привычек: {habits.count()}")

    for habit in habits:
        user_tg = habit.user.tg_chat_id
        print(f"Текущее время: {now} {habit.time} {now + timedelta(minutes=10)}")
        if user_tg and now < habit.time < now + timedelta(minutes=10):
            message = f"я буду {habit.action} в {habit.time} в {habit.place}"
            send_tg_message(user_tg, message)
