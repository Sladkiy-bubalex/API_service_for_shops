import re
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.http import Http404
from rest_framework.exceptions import PermissionDenied
from app.models import (
    Contact, User, ConfirmEmailToken,
    Shop, Category, Product, ProductInfo,
    ProductParameter, Order, OrderItem
)


class ContactSerializer(serializers.ModelSerializer):

    city = serializers.CharField(required=True)
    street = serializers.CharField(required=True)
    house = serializers.IntegerField(required=True)
    building = serializers.IntegerField()
    apartment = serializers.IntegerField()
    phone = serializers.CharField(required=True)
    
    class Meta:
        model = Contact
        fields = ["id", "user", "city", "street", "house", "building", "apartment", "phone"]
        read_only_fields = ("id", "user")

    def validate(self, attrs):
        phone = attrs.get("phone")
        if phone is not None:
            if not re.match(r"^\+7\d{10}$", phone):
                raise serializers.ValidationError("Номер телефона должен начинаться с +7 и содержать 11 цифр.")
        return attrs
    
    def create(self, validated_data):
        user = self.context["request"].user.id
        contact = Contact.objects.create(user_id=user, **validated_data)
        return contact


class UserSerializer(serializers.ModelSerializer):
    email = serializers.CharField(required=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    company = serializers.CharField()
    position = serializers.CharField()

    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email", "company", "position", "is_active", "type"]
        read_only_fields = ("id",)


class RegisterUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=True, write_only=True)
    email = serializers.CharField(required=True)
    username = serializers.CharField(required=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    type = serializers.CharField(required=False, allow_blank=True)
    company = serializers.CharField(required=False, allow_blank=True)
    position = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            "id", "password", "email", "first_name", "last_name",
            "username", "type", "company", "position"
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_email(self, value: str):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Этот email уже зарегистрирован.")
        return value
    
    def validate_username(self, value: str):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Такой никнейм уже существует")
        return value
    
    def validate_password(self, value: str):
        if len(value) < 8:
            raise serializers.ValidationError("Пароль должен содержать не менее 8 символов.")

        # Проверка на наличие цифр и букв
        if not re.search(r'[1-9]', value):
            raise serializers.ValidationError("Пароль должен содержать хотя бы одну цифру.")
        
        if not re.search(r'[A-Za-z]', value):
            raise serializers.ValidationError("Пароль должен содержать хотя бы одну букву.")

        return value


class ConfirmEmailSerializer(serializers.ModelSerializer):
    """Serializer для подтверждения почты."""

    key = serializers.CharField(required=True)
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=True
    )

    class Meta:
        model = ConfirmEmailToken
        fields = ["key", "user"]
    
    def validate(self, data: dict):
        key = data.get("key")
        user = data.get("user")
        activation_key = ConfirmEmailToken.objects.filter(
            user=user,
            key=key
        ).first()
        
        if not activation_key:
            raise serializers.ValidationError("Неверный ключ подтверждения Email")
        
        activation_key.user.is_active = True
        activation_key.user.save()
        activation_key.delete()
        return data


class LoginSerializer(serializers.ModelSerializer):
    """Serializer для авторизации"""

    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    token = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "token"]

    def validate(self, data: dict):
        # Проверяем наличие email и пароль,
        email = data.get("email")
        password = data.get("password")
        if email is None:
            raise serializers.ValidationError(
                "Для входа в систему требуется адрес электронной почты."
            )
        if password is None:
            raise serializers.ValidationError(
                "Для входа требуется пароль."
            )

        user = authenticate(username=email, password=password)
        if user is None:
            raise serializers.ValidationError(
                "Пользователь с таким адресом электронной почты и паролем не найден."
            )

        # Проверка активности пользователя.
        if not user.is_active:
            raise serializers.ValidationError(
                "Данная учетная запись не подтверждена или деактивирована."
                "Подтвердите эл. почту или обратитесь в поддержку"
            )

        # Метод validate должен возвращать словать проверенных данных.
        return {
            "email": user.email,
            "token": user.token
        }


class ProductParameterSerializer(serializers.ModelSerializer):
    """Serializer для параметра продукта"""

    id = serializers.IntegerField()
    
    class Meta:
        model = ProductParameter
        fields = ["id", "product_info", "parameter", "value"]
        read_only_fields = ("id", "product_info", "parameter")


class ProductSerializer(serializers.ModelSerializer):
    """Serializer для товара"""
    
    class Meta:
        model = Product
        fields = ["id", "name", "categories"]
        read_only_fields = ("id",)


class CategorySerializer(serializers.ModelSerializer):
    """Serializer для категории"""
    
    class Meta:
        model = Category
        fields = ["id", "name", "shops"]
        read_only_fields = ("id",)


class ShopSerializer(serializers.ModelSerializer):
    """Serializer для магазина"""
    
    class Meta:
        model = Shop
        fields = ["id", "name", "url", "user", "state"]
        read_only_fields = ("id",)


class ProductInfoSerializer(serializers.ModelSerializer):
    """Serializer для полной информации о товаре"""

    product = ProductSerializer(read_only=True)
    shop = ShopSerializer(read_only=True)
    product_parameters = ProductParameterSerializer(read_only=True, many=True)
    
    class Meta:
        model = ProductInfo
        fields = ["id", "product", "shop", "price", "price_rrc", "quantity", "product_parameters"]
        read_only_fields = ("id",)


class ProductInfoUpdateDestroySerializer(serializers.ModelSerializer):
    """Serializer для обновления и удаления информации о товаре"""

    product = ProductSerializer()
    shop = ShopSerializer()
    product_parameters = ProductParameterSerializer(many=True)

    class Meta:
        model = ProductInfo
        fields = ["id", "product", "shop", "price", "price_rrc", "quantity", "product_parameters"]
        read_only_fields = ("id",)

    def update(self, instance: ProductInfo, validated_data: dict):
        """Метод обновления экземпляра ProductInfo"""

        product_data = validated_data.pop("product", None)
        shop_data = validated_data.pop("shop", None)
        product_parameters_data = validated_data.pop("product_parameters", None)

        """ Обновляем информацию о продукте, если она была передана,
            если возникнет ошибка в процессе обновления
            то будет произведен откат изменений"""
        with transaction.atomic():
            if product_data:
                product_instance = instance.product
                ProductSerializer(product_instance).update(product_instance, product_data)

            if shop_data:
                shop_instance = instance.shop
                ShopSerializer(shop_instance).update(shop_instance, shop_data)

            if product_parameters_data:
                for data in product_parameters_data:
                    try:
                        product_parameter_instance = get_object_or_404(instance.product_parameters, id=data["id"])
                    except Http404:
                        raise Http404(f"Параметр продукта c id={data['id']} не найден")
                    ProductParameterSerializer(product_parameter_instance).update(product_parameter_instance, data)

            for attr, value in validated_data.items():
                setattr(instance, attr, value)

        instance.save()
        return instance


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer для элемента заказа"""

    id = serializers.IntegerField()
    
    class Meta:
        model = OrderItem
        fields = ["id", "order", "product_info", "quantity"]
        read_only_fields = ("id", "product_info")
        extra_kwargs = {
            "order": {
                "write_only": True
            },
            "quantity": {
                "min_value": 1,
                "max_value": 100,
                "error_messages": {
                    "min_value": "Количество товара должно быть не менее 1",
                    "max_value": "Количество товара должно быть не более 100"
                }
            }
        }


class OrderSerializer(serializers.ModelSerializer):
    """Serializer для заказа"""

    order_items = OrderItemSerializer(read_only=True, many=True)
    total_sum = serializers.IntegerField(read_only=True)
    contact = ContactSerializer(read_only=True)
    
    class Meta:
        model = Order
        fields = ["id", "user", "state", "contact", "order_items", "total_sum"]
        read_only_fields = ("id",)


class OrderUpdateDestroySerializer(serializers.ModelSerializer):
    """Serializer для обновления и удаления заказа"""

    contact = ContactSerializer()
    order_items = OrderItemSerializer(many=True)
    total_sum = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Order
        fields = ["id", "user", "state", "contact", "order_items", "total_sum"]
        read_only_fields = ("id",)
    
    def update(self, instance: Order, validated_data: dict):
        """Метод обновления экземпляра Order"""
        
        contact_data = validated_data.pop("contact", None)
        order_items_data = validated_data.pop("order_items", None)
        with transaction.atomic():
            if contact_data:
                contact_instance = instance.contact
                ContactSerializer(contact_instance).update(contact_instance, contact_data)
            
            if order_items_data:
                for data in order_items_data:
                    try:
                        order_item_instance = get_object_or_404(instance.order_items, id=data["id"])
                        # Проверка на принадлежность товара магазину пользователя
                        if order_item_instance.product_info.shop.user_id != self.context['request'].user.id:
                            raise PermissionDenied(f"Вы не можете изменять товар c id={data['id']}, так как он не принадлежит вашему магазину.")
                    except Http404:
                        raise Http404(f"Элемент заказа c id={data['id']} не найден")
                    OrderItemSerializer(order_item_instance).update(order_item_instance, data)
                
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            
            instance.save()
        
        return instance
