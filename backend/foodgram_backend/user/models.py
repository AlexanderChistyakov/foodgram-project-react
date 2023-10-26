from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


class User(AbstractUser):
    """Кастомная модель пользователя."""
    email = models.EmailField(unique=True,
                              verbose_name='Email')
    username = models.CharField(max_length=150,
                                unique=True,
                                verbose_name='Юзернейм',
                                null=False,
                                blank=False,
                                validators=[RegexValidator(
                                    regex=r'^[\w.@+-]+\Z',
                                )])
    first_name = models.CharField(max_length=150,
                                  verbose_name='Имя',
                                  null=False,
                                  blank=False)
    last_name = models.CharField(max_length=150,
                                 verbose_name='Фамилия',
                                 null=False,
                                 blank=False)


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
