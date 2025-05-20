import re
from rest_framework import serializers
from app.models import Contact, User, ConfirmEmailToken
from django.contrib.auth import authenticate


class ContactSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=True
    )
    city = serializers.CharField(required=True)
    street = serializers.CharField(required=True)
    house = serializers.IntegerField(required=True)
    building = serializers.IntegerField()
    apartment = serializers.IntegerField()
    phone = serializers.IntegerField(required=True)
    
    class Meta:
        model = Contact
        fields = ["id", "user", "city", "street", "house", "building", "apartment", "phone"]
        read_only_fields = ("id",)
        extra_kwargs = {
            'user': {'write_only': True}
        }


class GetUserSerializer(serializers.ModelSerializer):
    email = serializers.CharField(required=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    company = serializers.CharField()
    position = serializers.CharField()

    contact = ContactSerializer(read_only=True, many=True)

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

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Этот email уже зарегистрирован.")
        return value
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Такой никнейм уже существует")
        return value
    
    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Пароль должен содержать не менее 8 символов.")

        # Проверка на наличие цифр и букв
        if not re.search(r'[1-9]', value):
            raise serializers.ValidationError("Пароль должен содержать хотя бы одну цифру.")
        
        if not re.search(r'[A-Za-z]', value):
            raise serializers.ValidationError("Пароль должен содержать хотя бы одну букву.")

        return value

class ConfirmEmailSerializer(serializers.ModelSerializer):
    key = serializers.CharField(required=True)
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=True
    )

    class Meta:
        model = ConfirmEmailToken
        fields = ["key", "user"]
    
    def validate(self, data):
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
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    token = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "token"]

    def validate(self, data):
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
                "Данная учетная запись не подтверждена или деактивированна."
                "Подтвердите эл. почту или обратитесь в поддержку"
            )

        # Метод validate должен возвращать словать проверенных данных.
        return {
            "email": user.email,
            "username": user.username,
            "token": user.token
        }
