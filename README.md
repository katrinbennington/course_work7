**Название**: 
Трекер привычек с уведомлениями в Telegram

**Описание**:
Этот проект представляет собой приложение Django, которое позволяет пользователям отслеживать свои повседневные привычки и получать своевременные напоминания через Telegram. Приложение использует Celery для асинхронного планирования задач и встроенную систему аутентификации Django для управления пользователями.

**Требования**:
Python 3.8+
Django 3.2+
Celery 5.2+
Redis (for Celery broker and result backend)
Telegram Bot API

**Установка**:

1.
Клонируйте репозиторий:
git clone https://github.com/katrinbennington/course_work7.git
cd habit-tracker-with-tg-notifications

2.
Создайте виртуальную среду и активируйте ее:
python -m venv venv
source venv/bin/activate (for Unix/Linux)
venv\Scripts\activate (for Windows)

3.
Установите необходимые зависимости:
pip install -r requirements.txt

4.
Настройте базу данных:
python manage.py makemigrations
python manage.py migrate

5.
Создайте Telegram-бота и получите его API-токен:
Следуйте инструкциям на странице https://core.telegram.org/bots#creating-a-new-bot
Сохраните токен API для дальнейшего использования.

6.
Настройте бота Telegram в настройках Django:
Откройте config/settings.py.
Добавьте следующие строки в конец файла:
TELEGRAM_TOKEN = 'your_telegram_bot_token'
Замените «your_telegram_bot_token» фактическим токеном API, который вы получили на шаге 5.

7.
Запустите Celery worker:
celery -A config worker -l inf

8.
Запустите сервер разработки Django:
python manage.py runserver

Теперь вы можете получить доступ к приложению по адресу http://127.0.0.1:8000/.

Чтобы протестировать уведомления Telegram, создайте учетную запись пользователя, добавьте привычку и дождитесь запланированного уведомления.

Примечание. Это базовая реализация, и вам может потребоваться настроить ее в соответствии с вашими конкретными требованиями.
