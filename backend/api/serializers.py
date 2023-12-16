import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from recipes.models import (
    Favorite,
    Ingredient,
    IngredientsInRecipe,
    Recipe,
    ShoppingCart,
    Tag
)
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


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тега."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


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


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор краткой информации о рецепте."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор информации для избранного."""

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        user, recipe = data.get('user'), data.get('recipe')
        if self.Meta.model.objects.filter(user=user, recipe=recipe).exists():
            raise ValidationError(
                {'error': 'Этот рецепт уже добавлен в список'}
            )
        return data

    def to_representation(self, instance):
        context = {'request': self.context.get('request')}
        return ShortRecipeSerializer(instance.recipe, context=context).data


class ShoppingCartSerializer(FavoriteSerializer):
    """Сериализатор информации для списка покупок."""

    class Meta(FavoriteSerializer.Meta):
        model = ShoppingCart


class AddIngredientsInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор добавления ингредиента в описание рецепта."""
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientsInRecipe
        fields = ('id', 'amount')


class GetRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор получения данных о рецепте."""
    author = UsersInformationSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = IngredientsInRecipeSerializer(many=True)
    tags = TagSerializer(many=True)
    is_favourited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'image', 'ingredients', 'tags',
                  'is_favourited', 'is_in_shopping_cart',
                  'name', 'text', 'cooking_time')

    def get_is_favorited(self, object):
        user = self.context('request').user
        return user.is_authenticated and object.favorites.filter(
            user=user).exists()

    def get_is_in_shopping_cart(self, object):
        user = self.context('request').user
        return user.is_authenticated and object.shopping_cart.filter(
            user=user).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = AddIngredientsInRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, required=True
    )
    image = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = Recipe
        fields = [
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        ]

    def validate(self, attrs):
        ingredients = attrs.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                {'error': 'Выберите хотя бы 1 ингредиент!'}
            )
        unique_ingredients = [
            ingredient.get('id') for ingredient in ingredients
        ]
        if not unique_ingredients:
            raise serializers.ValidationError(
                {'error': 'Добавьте ингредиент'}
            )
        if len(unique_ingredients) != len(set(unique_ingredients)):
            raise ValidationError(
                {'error': 'Ингредиенты не должны повторяться'}
            )
        return attrs

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError(
                {'error': 'Выберите хотя бы 1 тег!'}
            )
        unique_tags = []
        for tag in tags:
            if tag in unique_tags:
                raise serializers.ValidationError(
                    {'error': 'Теги не должны повторяться!'}
                )
            unique_tags.append(tag)
        return tags

    def create_ingredient(self, ingredients_list, recipe):
        IngredientsInRecipe.objects.bulk_create(
            IngredientsInRecipe(
                ingredients=ingredient['id'],
                recipe=recipe,
                amount=ingredient['amount']
            ) for ingredient in ingredients_list
        )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = self.validate_tags(validated_data.pop('tags'))
        author = self.context.get('request').user
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredient(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        if 'tags' not in validated_data:
            raise serializers.ValidationError(
                {'error': 'Поле "tags" обязательно для обновления!'}
            )
        tags = validated_data.pop('tags')
        instance.ingredient.all().delete()
        instance.tags.set(tags)
        self.create_ingredient(ingredients, instance)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return GetRecipeSerializer(
            instance,
            context={'request': self.context.get('request')},
        ).data


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор подписок пользователя."""
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes(self, object):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = Recipe.objects.filter(author=object.author)
        if limit:
            queryset = queryset[:int(limit)]
        return ShortRecipeSerializer(queryset, many=True).data

    def get_is_subscribed(self, object):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return object.subscriber.filter(user=user).exists()

    def get_recipes_count(self, object):
        return object.recipes.count()
