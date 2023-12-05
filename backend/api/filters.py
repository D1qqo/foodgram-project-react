from django_filters import rest_framework as django_filter
from rest_framework import filters

from recipes.models import Ingredient, Recipe
from users.models import User


class IngredientFilter(django_filter.FilterSet):
    """Фильтрация по ингредиентам."""
    title = filters.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = 'title'


class RecipeFilter(django_filter.FilterSet):
    """Фильтрация по рецептам."""
    tags = django_filter.AllValuesMultipleFilter(field_name='tags__slug')
    favourite = django_filter.BooleanFilter(method='get_favourite_filter')
    shopping_list = django_filter.BooleanFilter(
        method='get_shopping_list_filter'
        )
    author = django_filter.ModelChoiceFilter(queryset=User.objects.all())

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
