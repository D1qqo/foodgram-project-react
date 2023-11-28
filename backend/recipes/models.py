from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

from core.models import AbstractModel

User = get_user_model()


class Ingredient(AbstractModel):
    """Модель ингредиента."""
    unit_measurement = models.CharField(
        verbose_name='Единица измерения',
        max_length=256
    )

    class Meta:
        ordering = ['title']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return (
            f'Название: {self.title},'
            f'Единица измерения: {self.unit_measurement}'
        )


class Tag(models.Model):
    """Модель тега."""
    title = models.CharField(
        verbose_name='Название',
        max_length=256,
        unique=True
    )
    color = models.CharField(
        verbose_name='Цвет',
        max_length=16
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        max_length=256,
        unique=True
    )

    class Meta:
        ordering = ['title']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return f'Название: {self.title}'


class Recipe(AbstractModel):
    """Модель рецепта."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipes/'
    )
    description = models.TextField(
        verbose_name='Описание'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        verbose_name="Ингредиенты",
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name="Теги",
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время готовки',
        validators=[MinValueValidator(
            limit_value=1,
            message='Время приготовления не может быть меньше 1 минуты')
        ]
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'Название: {self.title}'


class IngredientsInRecipe(models.Model):
    """Модель для связи таблиц ингредиентов и рецепта."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_list',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(
            limit_value=0.1,
            message='Количество ингредиентов не может быть меньше 0.1')
        ]
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'

    def __str__(self):
        return (
            f'Название ингредиента: {self.ingredient.title},'
            f'Единица измерения: {self.ingredient.unit_measurement} '
            f'в количестве {self.amount}'
        )


class Favourites(models.Model):
    """Модель избранного."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favourites',
        verbose_name='Список избранного у пользователя'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favourites',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favourite'
            )
        ]

    def __str__(self):
        return (
            f'Рецепт "{self.recipe}" был добавлен '
            f'пользователем {self.user} в избранное'
        )


class ShoppingList(models.Model):
    """Модель списка покупок."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_list',
        verbose_name='Список избранного у пользователя'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_list',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_list'
            )
        ]

    def __str__(self):
        return (
            f'Рецепт {self.recipe} был добавлен '
            f'в список покупок пользователем {self.user}'
        )
