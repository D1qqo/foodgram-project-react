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
    favourite = filters.BooleanFilter(method='get_favourite_filter')
    shopping_list = filters.BooleanFilter(
        method='get_shopping_list_filter'
        )
    author = filters.ModelChoiceFilter(queryset=User.objects.all())

    class Meta:
        model = Recipe
        fields = ('tags', 'favourite', 'shopping_list', 'author')

    def get_favourite_filter(self, queryset, title, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(favourites__user=self.request.user)
        return queryset

    def get_shopping_list_filter(self, queryset, title, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(shopping_list__user=self.request.user)
        return queryset.all()
