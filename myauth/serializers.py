from rest_framework import serializers
from django.contrib.auth.hashers import make_password

from myauth.models import User


class RegisterSerializer(serializers.ModelSerializer):
    """Сериализатор регистрации пользователя"""
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'password2']

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Пароли не совпадают")
        return data

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        user = User.objects.create(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password']
        )
        return user


class LoginSerializer(serializers.Serializer):
    """Сериализатор для авторизации пользователя."""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class LogoutSerializer(serializers.Serializer):
    """Сериализатор для выхода"""
    refresh_token = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор отображения информации о пользователе"""
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']
        read_only_fields = ['email']


class UserUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор обновления данных пользователя"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name']
