from rest_framework.permissions import BasePermission


class IsSelfUserOrAdmin(BasePermission):
    """
    Пользователь может получить доступ к своим данным или данным других пользователей, если он администратор.
    """

    def has_object_permission(self, request, view, obj):
        # Позволяем доступ, если пользователь администратор или запрашивает свои данные
        return request.user.is_staff or obj.id == request.user.id


class IsShopOwnerOrAdmin(BasePermission):
    """
    Пользователь может получить доступ к своим магазинам или магазинам других пользователей, если он администратор.
    """

    def has_object_permission(self, request, view, obj):
        # Позволяем доступ, если пользователь является владельцем магазина или администратором
        return request.user.is_staff or obj.user == request.user


class IsProductInfoOwnerOrAdmin(BasePermission):
    """
    Пользователь может получить доступ к своим товарам или товарам других пользователей, если он администратор.
    """

    def has_object_permission(self, request, view, obj):
        # Позволяем доступ, если пользователь является владельцем товара или администратором
        return request.user.is_staff or obj.shop.user == request.user


class IsCategoryOwnerOrAdmin(BasePermission):
    """
    Пользователь может получить доступ к своим категориям или категориям других пользователей, если он администратор.
    """

    def has_object_permission(self, request, view, obj):
        # Позволяем доступ, если пользователь является владельцем категории или администратором
        return request.user.is_staff or obj.shops.filter(user=request.user).exists()


class IsContactOwnerOrAdmin(BasePermission):
    """
    Пользователь может получить доступ к своим контактам или контактам других пользователей, если он администратор.
    """

    def has_object_permission(self, request, view, obj):
        # Позволяем доступ, если пользователь является владельцем контакта или администратором
        return request.user.is_staff or obj.user == request.user