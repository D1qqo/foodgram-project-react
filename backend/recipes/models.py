from django.core.validators import MinValueValidator
from django.db import models

from colorfield.fields import ColorField

from core.models import AbstractModel
from users.models import User


class Ingredient(AbstractModel):
    """Модель ингредиента."""
    measurement_unit = models.CharField(
        max_length=256,
        verbose_name='Единица измерения'
    )

    class Meta:
        ordering = ('name',)
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
        max_length=256,
        unique=True,
        verbose_name='Название'
    )
    color = ColorField(
        max_length=7,
        unique=True,
        default='#FF0000',
        verbose_name='Цвет'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Слаг'
    )

    class Meta:
        unique_together = ('name', 'slug')
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return f'Название: {self.name}, слаг {self.slug}'


class Recipe(AbstractModel):
    """Модель рецепта."""
    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='recipes',
        verbose_name='Автор'
    )
    image = models.ImageField(
        null=True,
        blank=False,
        upload_to='recipes/image',
        verbose_name='Картинка'
    )
    text = models.TextField(
        blank=False,
        verbose_name ='Описание'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        through='recipes.IngredientsInRecipe',
        verbose_name='Ингредиент'
    )
    tags = models.ManyToManyField(
        Tag,
        blank=False,
        related_name='recipes',
        verbose_name='Тег'
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(
            limit_value=1,
            message='Время приготовления не может быть меньше 1 минуты')
        ],
        verbose_name='Время готовки'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Время публикации'
    )

    class Meta:
        ordering = ('-pub_date',)
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
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(
            limit_value=0.1,
            message='Количество ингредиентов не может быть меньше 0.1')
        ],
        verbose_name='Количество'
    )

    class Meta:
        ordering = ('recipe__name',)

    def __str__(self):
        return (
            f'Название рецепта: {self.recipe}, '
            f'Ингредиент: {self.ingredients} '
            f'в количестве {self.amount}'
        )


class Favorite(models.Model):
    """Модель избранного."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return (
            f'Рецепт {self.recipe}, '
            f'пользовать {self.user}'
        )


class ShoppingCart(models.Model):
    """Модель списка покупок."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        default_related_name = 'shopping_cart'
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart'
            )
        ]

    def __str__(self):
        return (
            f'Рецепт {self.recipe}, '
            f'Пользователь {self.user}'
        )
