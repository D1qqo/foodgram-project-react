from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint
from colorfield.fields import ColorField

from core.models import AbstractModel
from users.models import User


class Ingredient(AbstractModel):
    """Модель ингредиента."""
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=256
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return (
            f'Название: {self.name},'
            f'Единица измерения: {self.measurement_unit}'
        )


class Tag(models.Model):
    """Модель тега."""
    name = models.CharField(
        verbose_name='Название',
        max_length=256,
        unique=True
    )
    color = ColorField(
        verbose_name='Цвет',
        max_length=16,
        unique=True,
        default='#FF0000'
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        max_length=256,
        unique=True
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return f'Название: {self.name}, слаг {self.slug}'


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
        through='recipes.IngredientsInRecipe',
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
        return f'Название: {self.name}'


class IngredientsInRecipe(models.Model):
    """Модель для связи таблиц ингредиентов и рецепта."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient',
        verbose_name='Рецепт'
    )
    ingredients = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe',
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
            f'Название рецепта: {self.recipe},'
            f'Ингредиент: {self.ingredient} '
            f'в количестве {self.amount}'
        )


class Favourite(models.Model):
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
