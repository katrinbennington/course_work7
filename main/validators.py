from datetime import timedelta

from rest_framework.serializers import ValidationError


class RewardHabitValidator:
    def __init__(self, field1, field2):
        self.field1 = field1
        self.field2 = field2

    def __call__(self, value):
        tmp_val1 = dict(value).get(self.field1)
        tmp_val2 = dict(value).get(self.field2)
        if tmp_val1 and tmp_val2:
            raise ValidationError(
                "Невозможен одновременный выбор связанной привычки и указания вознаграждения."
            )


class RelatedHabitValidator:
    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        tmp_val = dict(value).get(self.field)
        if tmp_val:
            if not tmp_val.is_pleasent:
                raise ValidationError(
                    "В связанные привычки могут попадать только привычки с признаком приятной привычки."
                )


class DurationTimeHabitValidator:
    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        tmp_val = dict(value).get(self.field)
        print(tmp_val)
        if tmp_val is not None and tmp_val > timedelta(seconds=120):
            raise ValidationError("Время выполнения должно быть не больше 120 секунд")


class PleasentHabitValidator:
    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        tmp_val = dict(value).get(self.field)
        if tmp_val:
            our_value = dict(value)
            if (
                    our_value.get("reward") is not None
                    or our_value.get("related_habit") is not None
            ):
                raise ValidationError(
                    "У приятной привычки не может быть вознаграждения или связанной привычки."
                )


class RegularityHabitValidator:
    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        frequency_in_days = dict(value).get(self.field)
        if 7 < frequency_in_days or frequency_in_days < 1:
            raise ValidationError("Нельзя выполнять привычку реже, чем 1 раз в 7 дней.")
