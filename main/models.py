from django.db import models

from config import settings
from users.models import User

NULLABLE = {"blank": True, "null": True}


class Habit(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                              verbose_name="Пользователь")
    place = models.CharField(max_length=100, verbose_name="Место")
    time = models.TimeField(verbose_name="Время")
    action = models.CharField(max_length=100, verbose_name="Действие")
    is_pleasent = models.BooleanField(default=False, verbose_name="Приятная привычка")
    associated_habit = models.ForeignKey('self', on_delete=models.CASCADE, **NULLABLE,
                                         verbose_name="Связанная привычка")
    frequency = models.CharField(default='daily', max_length=40, verbose_name='Периодичность',
                                 choices=(('daily', 'раз в день'),
                                          ('weekly', 'раз в неделю'),
                                          ('monthly', 'раз в месяц')))
    frequency_in_days = models.SmallIntegerField(null=True, blank=True,verbose_name="Количество раз")
    reward = models.CharField(max_length=100, verbose_name="Вознаграждение", **NULLABLE)
    time_doing = models.DurationField(max_length=2, verbose_name="Время на выполнение")
    is_public = models.BooleanField(default=False, verbose_name="Признак публичности")

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"

        def __str__(self):
            return f'{self.action}: {self.time} - {self.place}'
