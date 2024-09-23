from rest_framework.permissions import BasePermission


class IsAuthor(BasePermission):
    """ Класс проверка на автора """

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
