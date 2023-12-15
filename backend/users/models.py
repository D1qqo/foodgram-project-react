from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import UniqueConstraint

MAX_EMAIL_LENGTH = 254
MAX_ROLE_LENGTH = 5
MAX_NAME_LENGTH = 150
VALID_NAME = RegexValidator(r'^[\w.@+-]+\Z')


class User(AbstractUser):
    USER = 'user'
    ADMIN = 'admin'

    ROLE_CHOICES = [
        (USER, 'Пользователь'),
        (ADMIN, 'Администратор')
    ]

    email = models.EmailField(
        'Email',
        max_length=MAX_EMAIL_LENGTH,
        unique=True
    )
    username = models.CharField(
        'Имя пользователя',
        max_length=MAX_NAME_LENGTH,
        unique=True,
        blank=False,
        validators=[VALID_NAME],
    )
    first_name = models.CharField(
        'Имя',
        max_length=MAX_NAME_LENGTH,
        blank=False
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=MAX_NAME_LENGTH,
        blank=False
    )
    role = models.CharField(
        'Права пользователя',
        choices=ROLE_CHOICES,
        default=USER,
        max_length=MAX_ROLE_LENGTH
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name',
    ]

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_staff


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE,
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        related_name='author',
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            UniqueConstraint(
                fields=['user', 'author'],
                name='user_author_unique'
            )
        ]

    def __str__(self):
        return self.user, self.author

    def clean(self):
        if self.user == self.author:
            raise ValidationError(
                {'title': 'Нельзя подписаться на самого себя!'}
            )
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
