from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from reportlab.pdfbase import pdfmetrics, ttfonts
from reportlab.pdfgen import canvas
from rest_framework import status, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import PagePagination
from api.permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from api.serializers import (FavouritesSerializer, IngredientSerializer,
                             GetRecipeSerializer,
                             PostUpdateRecipeSerializer,
                             ShoppingListSerializer, TagSerializer)
from .models import (Ingredient, IngredientsInRecipe,
                     Recipe, Tag)


class IngredientViewSet(ReadOnlyModelViewSet):
    """Вьюсет ингредиента."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filterset_class = IngredientFilter
    filter_backends = (DjangoFilterBackend,)


class TagViewSet(ReadOnlyModelViewSet):
    """Вьюсет тега."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет рецепта."""
    queryset = Recipe.objects.all()
    serializer_class = GetRecipeSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = PagePagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def create(self, request):
        if request.user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = PostUpdateRecipeSerializer(
            data=request.data, context={'request': request}
        )
        if serializer.is_valid(raise_exception=True):
            recipe = serializer.save()
            return Response(
                GetRecipeSerializer(
                    recipe, context={'request': request}
                ).data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return GetRecipeSerializer
        return PostUpdateRecipeSerializer

    def create_fav_shop(self, request, pk, current_ser):
        user = request.user
        if not Recipe.objects.filter(pk=pk).exists():
            return Response({'error': 'Этого рецепта нет в списке'},
                            status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'POST':
            serializer = current_ser(
                data={'user': user.id, 'recipe': pk},
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_fav_shop(self, request, pk, current_ser):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        object = current_ser.Meta.model.objects.filter(
            user=user, recipe=recipe
        )
        if request.method == 'DELETE':
            if object.exists():
                object.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'error': 'Этого рецепта нет в списке'},
                                status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def favourite(self, request, pk):
        if request.method == 'POST':
            return self.create_fav_shop(request, pk, FavouritesSerializer)
        elif request.method == 'DELETE':
            return self.delete_fav_shop(request, pk, FavouritesSerializer)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(permissions.IsAuthenticatedOrReadOnly,)
    )
    def shopping_list(self, request, pk):
        if request.method == 'POST':
            return self.create_fav_shop(request, pk, ShoppingListSerializer)
        elif request.method == 'DELETE':
            return self.delete_fav_shop(request, pk, ShoppingListSerializer)

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_list(self, request):
        if request.user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        ingredients = (IngredientsInRecipe.objects.filter(
            recipe__shopping_list__user=request.user
        ).order_by('ingredients__name').values(
            'ingredients__name', 'ingredients__measurement_unit'
        ).annotate(amount=Sum('amount')))
        ingr_list = []
        ingr_list += 'Список покупок:\n  '
        for ingredient in ingredients:
            ingr_list.append(
                f'\n'
                f'{ingredient.get("ingredients__name").title()}:  '
                f'{ingredient.get("amount") }'
                f'({ingredient.get("ingredients__measurement_unit")}) '
            )
        response = FileResponse(
            ingr_list,
            content_type='text/plain'
        )
        response['Content-Disposition'] = (
            'attachment; filename=Shopping_List.txt'
        )
        return response
