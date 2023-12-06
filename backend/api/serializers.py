import base64

from django.core.files.base import ContentFile
from rest_framework import exceptions, serializers

from recipes.models import (Favourites, Ingredient, IngredientsInRecipe,
                            Recipe, ShoppingList, Tag)
from users.models import User


class Base64ImageField(serializers.ImageField):
    """Сериализатор кодирования изображения."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиента."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientsInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов в рецепте."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    title = serializers.ReadOnlyField(source='ingredient.title')
    unit_measurement = serializers.ReadOnlyField(
        source='ingredient.unit_measurement'
    )

    class Meta:
        model = IngredientsInRecipe
        fields = ('id', 'title', 'unit_measurement', 'amount')


class AddIngredientsInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор добавления ингредиента в описание рецепта."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
        )

    class Meta:
        model = IngredientsInRecipe
        fields = ('id', 'amount')


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тега."""

    class Meta:
        model = Tag
        fields = '__all__'


class GetRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор получения данных о рецепте."""
    author = UsersSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = AddIngredientsInRecipeSerializer(many=True)
    tags = TagSerializer(many=True)
    is_favourite = serializers.SerializerMethodField()
    is_shopping_list = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_is_favourite(self, recipe):
        user = self.context('request').user
        return user.is_authenticated and recipe.favourites.filter(
            user=user).exists()

    def get_is_shopping_list(self, recipe):
        user = self.context('request').user
        return user.is_authenticated and recipe.shopping_list.filter(
            user=user).exists()


class PostUpdateRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор публикации и изменения рецепта."""
    author = UsersSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = AddIngredientsInRecipeSerializer(many=True)
    tags = TagSerializer(many=True)

    class Meta:
        model = Recipe
        fields = '__all__'

    def validate_ingredients(self, value):
        if not value:
            raise exceptions.ValidationError(
                'Нужен хотя бы один ингредиент'
            )
        ingredients = [component['id'] for component in value]
        for ingredient in ingredients:
            if ingredients.count(ingredient) > 1:
                raise exceptions.ValidationError(
                    'Ингредиенты в рецепте не должны повторяться'
                )
        return value

    def validate_tags(self, value):
        if not value:
            raise exceptions.ValidationError('Добавьте хотя бы один тег!')
        return value

    def post(self, validated_data):
        pass

    def update(self, validated_data):
        pass


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор краткой информации о рецепте."""

    class Meta:
        model = Recipe
        fields = ('id', 'title', 'image', 'cooking_time')


class ShoppingListSerializer(serializers.ModelSerializer):
    """Сериализатор списка покупок."""

    class Meta:
        model = ShoppingList
        fields = ('user', 'recipe')
