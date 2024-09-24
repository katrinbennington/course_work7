from rest_framework.serializers import ModelSerializer

from main.models import Habit
from main.validators import (
    RewardHabitValidator,
    RelatedHabitValidator,
    DurationTimeHabitValidator,
    PleasentHabitValidator,
    RegularityHabitValidator,
)


class HabitSerializer(ModelSerializer):
    class Meta:
        model = Habit
        fields = "__all__"
        validators = [
            RewardHabitValidator(field1="reward", field2="associated_habit"),
            RelatedHabitValidator(field="associated_habit"),
            DurationTimeHabitValidator(field="time_doing"),
            PleasentHabitValidator(field="is_pleasent"),
            RegularityHabitValidator(field="frequency_in_days"),
        ]
