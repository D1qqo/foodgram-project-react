from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import UniqueConstraint

MAX_LENGTH_EMAIL = 254
MAX_LENGTH_NAME = 150


class User(AbstractUser):
    """Модель пользователя."""
    email = models.EmailField(
        unique=True,
        max_length=MAX_LENGTH_EMAIL,
        verbose_name='Электронная почта'
    )
    username = models.CharField(
        max_length=MAX_LENGTH_NAME,
        unique=True,
        verbose_name='Логин',
        validators=[RegexValidator(r'^[\w.@+-]+\Z'), ]
    )
    first_name = models.CharField(
        max_length=MAX_LENGTH_NAME,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=MAX_LENGTH_NAME,
        verbose_name='Фамилия'
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username',
                       'first_name',
                       'last_name'
                       )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'Пользователь: {self.username}'


class Subscribe(models.Model):
    """Модель подписки."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscriber'
            )
        ]

    def __str__(self):
        return f'У автора {self.author} подписчик: {self.user}'
