import base64

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import exceptions, serializers

from recipes.models import (Favourites, Ingredient, IngredientsInRecipe,
                            Recipe, ShoppingList, Tag)
from users.models import Subscribe, User


class Base64ImageField(serializers.ImageField):
    """Сериализатор кодирования изображения."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class UsersCreateSerializer(UserCreateSerializer):
    """Сериализатор создания пользователя."""

    class Meta:
        model = User
        fields = ('id', 'email', 'username',
                  'first_name', 'last_name', 'password')


class UsersInformationSerializer(UserSerializer):
    """Сериализатор информации о пользователях."""
    is_subscribe = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username',
                  'first_name', 'last_name', 'is_subscribe')

    def get_is_subscribe(self, object):
        user = self.context.get('request').user.id
        return Subscribe.objects.filter(
            author=object.id, user=user).exists()


class FavouritesSerializer(serializers.ModelSerializer):
    """Сериализатор краткой информации для избранного."""
    image = Base64ImageField()

    class Meta:
        model = Favourites
        fields = ('id', 'title', 'image', 'cooking_time')


class SubscribeSerializer(UsersInformationSerializer):
    """Сериализатор подписок пользователя."""
    recipes = serializers.SerializerMethodField()
    count_recipes = serializers.SerializerMethodField()

    class Meta:
        model = Subscribe
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'count_recipes')

    def get_recipes(self, object):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = Recipe.objects.filter(author=object.author)
        if limit:
            queryset = queryset[:int(limit)]
        return FavouritesSerializer(queryset, many=True).data

    def get_count_recipes(self, object):
        return object.recipes.count()


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиента."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientsInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов в рецепте."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.title')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientsInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


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
        fields = ('id', 'title', 'color', 'slug')


class GetRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор получения данных о рецепте."""
    author = UsersInformationSerializer(read_only=True)
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
    author = UsersInformationSerializer(read_only=True)
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
        amount_ingredients = []
        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            amount = ingredient.get('amount')
            ingredient = get_object_or_404(
                Ingredient, pk=ingredient.get('id').id
            )
        amount_ingredients.append(IngredientsInRecipe(
            recipe=recipe, ingredient=ingredient, amount=amount))
        IngredientsInRecipe.objects.bulk_create(amount_ingredients)
        return recipe

    def update(self, example, validated_data):
        tags = validated_data.pop('tags', None)
        if tags is not None:
            example.tags.set(tags)
        ingredients = validated_data.pop('ingredients', None)
        if ingredients is not None:
            example.ingredients.clear()
            for ingredient in ingredients:
                amount = ingredient.get('amount')
                ingredient = get_object_or_404(
                    Ingredient, pk=ingredient.get('id').id
                )
                IngredientsInRecipe.objects.update_or_create(
                    recipe=example,
                    ingredient=ingredient,
                    defaults={'amount': amount},
                )
        return super().update(example, validated_data)

    def representation(self, example):
        serializer = GetRecipeSerializer(
            example, context={'request': self.context.get('request')}
        )
        return serializer.data


class ShoppingListSerializer(serializers.ModelSerializer):
    """Сериализатор списка покупок."""

    class Meta:
        model = ShoppingList
        fields = ('user', 'recipe')
