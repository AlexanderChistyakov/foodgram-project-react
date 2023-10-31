from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from user.models import Follow, User


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор создания пользователя."""

    class Meta:
        model = User
        fields = (
            'id', 'first_name', 'last_name', 'username', 'email', 'password'
        )
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'username': {'required': True},
            'email': {'required': True},
            'password': {'required': True}
        }


class CustomUserSerializer(UserSerializer):
    """Сериализатор пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id',
            'username', 'first_name',
            'last_name', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        """Проверка наличия подписки."""

        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=request.user, author=obj
        ).exists()
