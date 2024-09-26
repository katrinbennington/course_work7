from datetime import timedelta, datetime
from celery import shared_task
from django.utils import timezone

from main.models import Habit
from main.services import send_tg_message


@shared_task()
def tg_notification():
    current_time = timezone.now()
    current_time_less = current_time - timedelta(minutes=5)
    habits = Habit.objects.filter(time__lte=current_time.time(), time__gte=current_time_less.time())
    for habit in habits:
        user_tg = habit.user.tg_chat_id
        message = f"я буду {habit.action} в {habit.time} в {habit.place}"
        send_tg_message(user_tg, message)
