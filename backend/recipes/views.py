from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import PagePagination
from api.permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from api.serializers import (
    FavoriteSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeSerializer,
    ShoppingCartSerializer,
    TagSerializer
)
from .models import (
    Ingredient,
    IngredientsInRecipe,
    Recipe,
    Tag
)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = PagePagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def create(self, request):
        if request.user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = RecipeCreateSerializer(
            data=request.data, context={'request': request}
        )
        if serializer.is_valid(raise_exception=True):
            recipe = serializer.save()
            return Response(
                RecipeSerializer(
                    recipe, context={'request': request}
                ).data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return RecipeCreateSerializer

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
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.create_fav_shop(request, pk, FavoriteSerializer)
        elif request.method == 'DELETE':
            return self.delete_fav_shop(request, pk, FavoriteSerializer)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(IsAuthenticatedOrReadOnly,)
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.create_fav_shop(request, pk, ShoppingCartSerializer)
        elif request.method == 'DELETE':
            return self.delete_fav_shop(request, pk, ShoppingCartSerializer)

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        if request.user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        ingredients = (IngredientsInRecipe.objects.filter(
            recipe__shopping_cart__user=request.user
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
            'attachment; filename=Shopping_Cart.txt'
        )
        return response
