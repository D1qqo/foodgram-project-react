from django_filters.rest_framework import filters, FilterSet

from recipes.models import Ingredient, Recipe
from users.models import User


class IngredientFilter(FilterSet):
    """Фильтрация по ингредиентам."""
    name = filters.CharFilter(field_name='name', lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit')


class RecipeFilter(FilterSet):
    """Фильтрация по рецептам."""
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(method='get_favorited_filter')
    is_shopping_cart = filters.BooleanFilter(
        method='get_shopping_cart_filter'
        )
    author = filters.ModelChoiceFilter(queryset=User.objects.all())

    class Meta:
        model = Recipe
        fields = ('tags', 'is_favorited', 'is_shopping_cart', 'author')

    def get_favorited_filter(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def get_shopping_cart_filter(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset.all()
