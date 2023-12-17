from django.db.models import Sum
from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.pdfbase import pdfmetrics, ttfonts
from reportlab.pdfgen import canvas
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
    PostUpdateRecipeSerializer,
    GetRecipeSerializer,
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
    """Вьюсет ингредиента."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет тега."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None


class RecipesViewSet(viewsets.ModelViewSet):
    """Вьюсет рецепта."""
    queryset = Recipe.objects.all()
    serializer_class = GetRecipeSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = PagePagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return GetRecipeSerializer
        return PostUpdateRecipeSerializer

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
        return self.post_delete(pk, FavoriteSerializer)

    @action(methods=['POST', 'DELETE'], detail=True)
    def shopping_list(self, request, pk):
        return self.post_delete(pk, ShoppingCartSerializer)

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
            'ingredients__name', 'amount', 'ingredients__measurement_unit')

        ingredients_list = {}
        for name, amount, measurement_unit in ingredients:
            if name not in ingredients_list:
                ingredients_list[name] = {
                    'amount': amount, 'measurement_unit': measurement_unit
                    }
            else:
                ingredients_list[name]['amount'] += amount
        height = 700

        p.drawString(100, 750, 'Список покупок')
        for i, (name, data) in enumerate(ingredients_list.items(), start=1):
            p.drawString(
                80, height,
                f"{i}. {name} – {data['amount']} {data['measurement_unit']}")
            height -= 25
        p.showPage()
        p.save()
        return response
