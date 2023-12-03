from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import UniqueConstraint


class User(AbstractUser):
    """Класс пользователя."""
    email = models.EmailField(
        unique=True,
        max_length=256,
        verbose_name='Электронная почта'
    )
    username = models.CharField(
        max_length=256,
        unique=True,
        verbose_name='Логин'
    )
    first_name = models.CharField(
        max_length=256,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=256,
        verbose_name='Фамилия'
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username',
                       'first_name',
                       'last_name',
                       'password'
                       ]

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'Пользователь: {self.username}'


class Subscribe(models.Model):
    """Класс подписки."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribing',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscribe'
            )
        ]

    def __str__(self):
        return f'У автора {self.author} подписчик: {self.user}'
