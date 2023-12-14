import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import exceptions, serializers

from recipes.models import (Favourite, Ingredient, IngredientsInRecipe,
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
        model = Favourite
        fields = ('id', 'name', 'image', 'cooking_time', 'recipe', 'user')


class SubscribeSerializer(UsersInformationSerializer):
    """Сериализатор подписок пользователя."""
    recipes = serializers.SerializerMethodField()
    count_recipes = serializers.SerializerMethodField()

    class Meta:
        model = Subscribe
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribe', 'recipes', 'count_recipes')

    def get_recipe(self, object):
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
    id = serializers.ReadOnlyField(source='ingredients.id')
    name = serializers.ReadOnlyField(source='ingredients.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit'
    )
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientsInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class AddIngredientsInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор добавления ингредиента в описание рецепта."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
        )

    class Meta:
        model = IngredientsInRecipe
        fields = ('id', 'amount')


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тега."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


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
        fields = ('id', 'author', 'image', 'ingredients', 'tags',
                  'is_favourites', 'is_shopping_list',
                  'name', 'description', 'cooking_time')

    def get_is_favourites(self, object):
        user = self.context('request').user
        return user.is_authenticated and object.favourites.filter(
            user=user).exists()

    def get_is_shopping_list(self, object):
        user = self.context('request').user
        return user.is_authenticated and object.shopping_list.filter(
            user=user).exists()


class PostUpdateRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор публикации и изменения рецепта."""
    image = Base64ImageField()
    ingredients = AddIngredientsInRecipeSerializer(many=True)
    tags = TagSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ('image', 'ingredients', 'tags',
                  'name', 'description', 'cooking_time')

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
            raise exceptions.ValidationError('Добавьте хотя бы один тег')
        return value

    def set_tags_ingredients(self, recipe, tags, ingredients):
        recipe.tags.set(tags)
        for ingredient in ingredients:
            IngredientsInRecipe.objects.bulk_create([
                IngredientsInRecipe(
                    recipe=recipe,
                    ingredient=ingredient.get('id'),
                    amount=ingredient.get('amount'))
            ])

    def create(self, validated_data):
        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.set_tags_ingredients(recipe, tags, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        instance.ingredient.clear()
        tags = validated_data.pop('tags')
        self.set_tags_ingredients(instance, tags, ingredients)
        return super().update(instance, validated_data)

    def representation(self, example):
        serializer = GetRecipeSerializer(
            example, context={'request': self.context.get('request')}
        )
        return serializer.data


class ShoppingListSerializer(FavouritesSerializer):
    """Сериализатор списка покупок."""

    class Meta(FavouritesSerializer.Meta):
        model = ShoppingList
