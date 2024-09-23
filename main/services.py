from django.contrib.sites import requests

from config.settings import TELEGRAM_URL, TELEGRAM_TOKEN


def send_tg_message(chat_id, message):
    params = {
        'text': message,
        'chat_id': chat_id
    }
    response = requests.get(f'{TELEGRAM_URL}{TELEGRAM_TOKEN}/sendMessage', params=params)