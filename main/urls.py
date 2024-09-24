from django.urls import path

from main.apps import MainConfig
from main.views import (HabitCreateAPIView, HabitRetrieveAPIView, HabitDestroyAPIView, HabitListAPIView,
                        HabitPublicAPIView, HabitUpdateAPIView)

app_name = MainConfig.name

urlpatterns = [
    path('create/', HabitCreateAPIView.as_view(), name='create'),
    path('retrieve/<int:pk>/', HabitRetrieveAPIView.as_view(), name='get'),
    path('update/<int:pk>/', HabitUpdateAPIView.as_view(), name='update'),
    path('destroy/<int:pk>/', HabitDestroyAPIView.as_view(), name='delete'),
    path('list/', HabitListAPIView.as_view(), name='list'),
    path('list_public/', HabitPublicAPIView.as_view(), name='list_public'),  # Список публичных привычек
]
