import re
from rest_framework import serializers
from app.models import Contact, User


class ContactSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(required=True)
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


class RegisterUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=True, write_only=True)
    email = serializers.CharField(required=True)
    username = serializers.CharField(required=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    type = serializers.CharField()

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "username", "type"]
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
        if not re.search(r'd', value):
            raise serializers.ValidationError("Пароль должен содержать хотя бы одну цифру.")
        
        if not re.search(r'[A-Za-z]', value):
            raise serializers.ValidationError("Пароль должен содержать хотя бы одну букву.")

        return value


class GetUserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.CharField(required=True)
    company = serializers.CharField()
    position = serializers.CharField()

    contact = ContactSerializer(read_only=True, many=True)

    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email", "company", "position", "is_active", "type"]
        read_only_fields = ("id",)
    