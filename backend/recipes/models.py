from django.core.validators import MinValueValidator
from django.db import models

from colorfield.fields import ColorField

from users.models import User

MAX_NAME_LENGTH = 200
MAX_COLOR_LENGTH = 7
MIN_TIME_COOK = MinValueValidator(1)
MIN_AMOUNT_INGR = 1


class Ingredient(models.Model):
    name = models.CharField(
        'Название',
        max_length=MAX_NAME_LENGTH
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=MAX_NAME_LENGTH
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    name = models.CharField(
        'Название тега',
        max_length=MAX_NAME_LENGTH,
        unique=True
    )
    color = ColorField(
        'Цветовой HEX-код',
        max_length=MAX_COLOR_LENGTH,
        unique=True,
        default='#FF0000'
    )
    slug = models.SlugField(
        'Слаг',
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        unique_together = ('name', 'slug')

    def __str__(self):
        return f'{self.name}, {self.slug}'


class Recipes(models.Model):
    name = models.CharField(
        'Название рецепта',
        max_length=MAX_NAME_LENGTH
    )
    text = models.TextField(
        'Описание',
        blank=False
    )
    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='recipes',
        verbose_name='Автор'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        through='recipes.IngredientsInRecipe',
        verbose_name='Ингредиенты'
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipes/image',
        null=True,
        blank=False
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег',
        blank=False,
        related_name='recipes'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[MIN_TIME_COOK]
    )
    pub_date = models.DateTimeField(
        verbose_name='Время публикации',
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class IngredientsInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipes,
        verbose_name='рецепт',
        on_delete=models.CASCADE,
        related_name='ingredient'
    )
    ingredients = models.ForeignKey(
        Ingredient,
        verbose_name='ингредиент',
        related_name='recipe',
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField(
        validators=[MIN_TIME_COOK]
    )

    class Meta:
        ordering = ('recipe__name',)

    def __str__(self):
        return f'{self.recipe}, {self.ingredients}, {self.amount}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='favorites',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipes,
        verbose_name='Рецепт',
        related_name='favorites',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'

    def __str__(self):
        return f'{self.user} - {self.recipe}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipes,
        verbose_name='Рецепты',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        default_related_name = 'shopping_cart'

    def __str__(self):
        return f'{self.user} - {self.recipe}'
