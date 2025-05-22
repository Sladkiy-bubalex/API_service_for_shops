from rest_framework.permissions import BasePermission

class IsSelfOrAdmin(BasePermission):
    """
    Пользователь может получить доступ к своим данным или данным других пользователей, если он администратор.
    """

    def has_object_permission(self, request, view, obj):
        # Позволяем доступ, если пользователь администратор или запрашивает свои данные
        return request.user.is_staff or obj.id == request.user.id