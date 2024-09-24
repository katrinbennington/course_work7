from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import (CreateAPIView,
                                     ListAPIView,
                                     RetrieveAPIView,
                                     DestroyAPIView,
                                     UpdateAPIView)

from main.models import Habit
from main.paginators import HabitPaginator
from main.serializers import HabitSerializer
from main.permissions import IsOwner


class HabitCreateAPIView(CreateAPIView):
    """ Создание привычки """
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    pagination_class = HabitPaginator
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ("action",)
    ordering_fields = ("time",)

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user.pk).order_by("id")

    def perform_create(self, serializer):
        new_habit = serializer.save()
        new_habit.user = self.request.user
        new_habit.save()


class HabitRetrieveAPIView(RetrieveAPIView):
    """ Просмотр одной привычки """

    serializer_class = HabitSerializer
    queryset = Habit.objects.all()
    pagination_class = HabitPaginator

    def get_object(self):
        pk = self.kwargs.get('pk')
        return get_object_or_404(self.queryset, pk=int(pk))


class HabitUpdateAPIView(UpdateAPIView):
    """ Редактирование привычки """
    serializer_class = HabitSerializer
    queryset = Habit.objects.all()
    pagination_class = HabitPaginator


class HabitDestroyAPIView(DestroyAPIView):
    """ Удаление привычки """

    serializer_class = HabitSerializer
    queryset = Habit.objects.all()


class HabitListAPIView(ListAPIView):
    """ Список привычек """

    serializer_class = HabitSerializer
    queryset = Habit.objects.all()
    pagination_class = HabitPaginator


class HabitPublicAPIView(ListAPIView):
    """ Список публичных привычек """

    serializer_class = HabitSerializer
    queryset = Habit.objects.filter(is_public=True)
    permission_classes = [AllowAny]
