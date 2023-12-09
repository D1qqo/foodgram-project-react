from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.pdfbase import pdfmetrics, ttfonts
from reportlab.pdfgen import canvas
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import PagePagination
from api.permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from api.serializers import (FavouritesSerializer, IngredientSerializer,
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


class TagViewSet(ReadOnlyModelViewSet):
    """Вьюсет тега."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    """Вьюсет рецепта."""
    queryset = Recipe.objects.all()
    serializer_class = PostUpdateRecipeSerializer
    permission_classes = (IsAdminOrReadOnly | IsAuthorOrReadOnly,)
    pagination_class = PagePagination
    filterset_class = RecipeFilter

    def post_delete(self, pk, serializer_class):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        object = serializer_class.Meta.model.objects.filter(
            user=user, recipe=recipe
        )

        if self.request.method == 'POST':
            serializer = serializer_class(
                data={'user': user.id, 'recipe': pk},
                context={'request': self.request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == 'DELETE':
            if object.exists():
                object.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'error': 'Рецепт не находится в списке'},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST', 'DELETE'], detail=True)
    def favourite(self, request, pk):
        return self.post_delete(pk, FavouritesSerializer)

    @action(methods=['POST', 'DELETE'], detail=True)
    def shopping_list(self, request, pk):
        return self.post_delete(pk, ShoppingListSerializer)

    @action(detail=False)
    def download(self, request):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.pdf"'
        )
        p = canvas.Canvas(response)
        calibri = ttfonts.TTFont('Calibri', 'data/calibri.ttf')
        pdfmetrics.registerFont(calibri)
        p.setFont('Calibri', 14)

        ingredients = IngredientsInRecipe.objects.filter(
            recipe__shopping_list__user=request.user).values_list(
            'ingredient__title', 'amount', 'ingredient__unit_measurement')

        ingredients_list = {}
        for title, amount, unit_measurement in ingredients:
            if title not in ingredients_list:
                ingredients_list[title] = {
                    'amount': amount, 'unit_measurement': unit_measurement
                    }
            else:
                ingredients_list[title]['amount'] += amount
        height = 700

        p.drawString(100, 750, 'Список покупок')
        for i, (title, data) in enumerate(ingredients_list.items(), start=1):
            p.drawString(
                80, height,
                f"{i}. {title} – {data['amount']} {data['unit_measurement']}")
            height -= 25
        p.showPage()
        p.save()
        return response
