from django.shortcuts import get_object_or_404
from rest_framework.generics import (CreateAPIView,
                                     ListAPIView,
                                     RetrieveAPIView,
                                     DestroyAPIView,
                                     UpdateAPIView)
from rest_framework.permissions import AllowAny

from main.models import Habit
from main.paginators import HabitPaginator
from main.permissions import IsAuthor
from main.serializers import HabitSerializer


class HabitCreateAPIView(CreateAPIView):
    """ Создание привычки """
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    permission_classes = [AllowAny]

    # Функция привязывает автора к его привычке
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class HabitRetrieveAPIView(RetrieveAPIView):
    """ Просмотр одной привычки """

    serializer_class = HabitSerializer
    queryset = Habit.objects.all()
    pagination_class = HabitPaginator
    permission_classes = [IsAuthor]

    def get_object(self):
        pk = self.kwargs.get('pk')
        return get_object_or_404(self.queryset, pk=int(pk))


class HabitUpdateAPIView(UpdateAPIView):
    """ Редактирование привычки """
    serializer_class = HabitSerializer
    queryset = Habit.objects.all()
    pagination_class = HabitPaginator
    permission_classes = [IsAuthor]


class HabitDestroyAPIView(DestroyAPIView):
    """ Удаление привычки """

    serializer_class = HabitSerializer
    queryset = Habit.objects.all()
    permission_classes = [IsAuthor]

    def get_queryset(self):
        if IsAuthor().has_permission(self.request, self):
            return Habit.objects.all()
        else:
            return Habit.objects.filter(owner=self.request.user)


class HabitListAPIView(ListAPIView):
    """ Список привычек """

    serializer_class = HabitSerializer
    queryset = Habit.objects.all()
    pagination_class = HabitPaginator
    permission_classes = [IsAuthor]


class HabitPublicAPIView(ListAPIView):
    """ Список публичных привычек """

    serializer_class = HabitSerializer
    queryset = Habit.objects.filter(is_public=True)



