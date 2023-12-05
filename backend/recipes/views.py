from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import PagePagination
from api.permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from api.serializers import (IngredientSerializer, TagSerializer,
                             RecipeSerializer)
from .models import Ingredient, Tag, Recipe


class IngredientViewSet(ReadOnlyModelViewSet):
    """Вьюсет ингредиента."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = IsAdminOrReadOnly
    pagination_class = None
    filterset_class = IngredientFilter


class TagViewSet(ReadOnlyModelViewSet):
    """Вьюсет тега."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = IsAdminOrReadOnly
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    """Вьюсет рецепта."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAdminOrReadOnly | IsAuthorOrReadOnly)
    pagination_class = PagePagination
    filterset_class = RecipeFilter
