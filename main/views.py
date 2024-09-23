from django.shortcuts import get_object_or_404
from rest_framework.generics import (CreateAPIView,
                                     ListAPIView,
                                     RetrieveAPIView,
                                     DestroyAPIView,
                                     UpdateAPIView)

from main.models import Habit
from main.paginators import HabitPaginator
from main.permissions import IsAutor
from main.serializers import HabitSerializer


class HabitCreateAPIView(CreateAPIView):
    """ Создание привычки """

    serializer_class = HabitSerializer
    queryset = Habit.objects.all()

    # Функция привязывает автора к его привычке
    def perform_create(self, serializer):
        new_habit = serializer.save()
        new_habit.user = self.request.user
        new_habit.save()


class HabitRetrieveAPIView(RetrieveAPIView):
    """ Просмотр одной привычки """

    serializer_class = HabitSerializer
    queryset = Habit.objects.all()
    permission_classes = [IsAutor]

    def get_object(self):
        pk = self.kwargs.get('pk')
        return get_object_or_404(self.queryset, pk=int(pk))


class HabitUpdateAPIView(UpdateAPIView):
    """ Редактирование привычки """
    serializer_class = HabitSerializer
    queryset = Habit.objects.all()
    permission_classes = [IsAutor]


class HabitDestroyAPIView(DestroyAPIView):
    """ Удаление привычки """

    serializer_class = HabitSerializer
    queryset = Habit.objects.all()
    permission_classes = [IsAutor]


class HabitListAPIView(ListAPIView):
    """ Список привычек """

    serializer_class = HabitSerializer
    queryset = Habit.objects.all()
    pagination_class = HabitPaginator
    permission_classes = [IsAutor]


class HabitPublicAPIView(ListAPIView):
    """ Список публичных привычек """

    serializer_class = HabitSerializer
    queryset = Habit.objects.filter(is_public=True)



