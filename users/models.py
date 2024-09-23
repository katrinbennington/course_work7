from django.contrib.auth.models import AbstractUser
from django.db import models


NULLABLE = {"blank": True, "null": True}

class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, verbose_name="Email address")
    phone_number = models.CharField(max_length=35, verbose_name="Телефон", **NULLABLE,
                                    help_text="Введите номер телефона")
    country = models.CharField(max_length=100, verbose_name="Страна", **NULLABLE)
    avatar = models.ImageField(upload_to="users/photo", verbose_name="Аватар", help_text="Загрузите свой аватар",
                               **NULLABLE)

    tg_chat_id = models.CharField(
        max_length=50, verbose_name="Телеграм чат ID", **NULLABLE, help_text="Введите ID чата в Telegram для "
                                                                             "уведомлений")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email
