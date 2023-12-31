from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from utils.constants import USER_FIELDS_MAX_LENGTH


class User(AbstractUser):
    """Кастомная модель пользователя."""

    email = models.EmailField(
        unique=True,
        verbose_name='Email'
    )
    username = models.CharField(
        max_length=USER_FIELDS_MAX_LENGTH,
        unique=True,
        verbose_name='Юзернейм',
        validators=[
            RegexValidator(regex=r'^[\w.@+-]+\Z', )
        ]
    )
    first_name = models.CharField(
        max_length=USER_FIELDS_MAX_LENGTH,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=USER_FIELDS_MAX_LENGTH,
        verbose_name='Фамилия',
    )
    password = models.CharField(
        max_length=USER_FIELDS_MAX_LENGTH,
    )


class Follow(models.Model):
    """Модель подписок."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_author'
            )
        ]
