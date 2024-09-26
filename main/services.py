
from django.conf import settings
from django.utils.timezone import localtime

from rest_framework import status

import requests
from config import settings
from config.settings import TELEGRAM_URL, TELEGRAM_TOKEN


def send_tg_message(chat_id, message):
    params = {
            'text': message,
            'chat_id': chat_id
        }

    url = f'{TELEGRAM_URL}{TELEGRAM_TOKEN}/sendMessage'
    response = requests.get(url, params=params, timeout=10)
    if not response.ok:
        raise RuntimeError("Failed to sent telegram message")

# def send_tg_message(habit):
#     """Отправляет сообщение через телеграм с напоинанием о привычке"""
#     local_habit_time = localtime(habit.time)
#     formatted_time = local_habit_time.strftime("%H:%M")
#
#     text = f"{habit.action} запланировано на сегодня на {formatted_time}"
#     chat_id = habit.user.tg_chat_id
#     params = {"text": text, "chat_id": chat_id}
#
#     response = requests.get(
#         f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data=params
#     )
#     if response.status_code != status.HTTP_200_OK:
#         print(f"Ошибка при отправке сообщения в Telegram: {response.text}")
