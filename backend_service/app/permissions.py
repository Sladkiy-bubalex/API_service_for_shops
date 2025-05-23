from rest_framework.permissions import BasePermission


class IsSelfOrAdmin(BasePermission):
    """
    Пользователь может получить доступ к своим данным или данным других пользователей, если он администратор.
    """

    def has_object_permission(self, request, view, obj):
        # Позволяем доступ, если пользователь администратор или запрашивает свои данные
        return request.user.is_staff or obj.id == request.user.id


class IsShopOwner(BasePermission):
    """
    Пользователь может получить доступ к своим магазинам.
    """

    def has_object_permission(self, request, view, obj):
        # Позволяем доступ, если пользователь является владельцем магазина
        return obj.user == request.user


class IsProductOwner(BasePermission):
    """
    Пользователь может получить доступ к своим товарам.
    """

    def has_object_permission(self, request, view, obj):
        # Позволяем доступ, если пользователь является владельцем товара
        return obj.shop.user == request.user


class IsCategoryOwner(BasePermission):
    """
    Пользователь может получить доступ к своим категориям.
    """

    def has_object_permission(self, request, view, obj):
        # Позволяем доступ, если пользователь является владельцем категории
        return obj.shops.filter(user=request.user).exists()