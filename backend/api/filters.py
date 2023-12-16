from django_filters.rest_framework import FilterSet, filters

from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(FilterSet):
    name = filters.CharFilter(
        field_name='name', lookup_expr='istartswith',
    )

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    author = filters.NumberFilter(field_name='author')
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favourited = filters.BooleanFilter(
        method='get_filter_is_favourited',
    )
    is_in_shopping_list = filters.BooleanFilter(
        method='get_filter_is_in_shopping_list',
    )

    class Meta:
        model = Recipe
        fields = (
            'author',
            'tags',
            'is_favourited',
            'is_in_shopping_list',
        )

    def get_filter_is_favourited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favourites__user=self.request.user)
        return queryset

    def get_filter_is_in_shopping_list(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping_list__user=self.request.user)
        return queryset
