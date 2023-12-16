from django_filters.rest_framework import FilterSet, filters

from recipes.models import Ingredient, Recipes, Tag


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
    is_favorited = filters.BooleanFilter(
        method='get_filter_is_favorited',
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_filter_is_in_shopping_cart',
    )

    class Meta:
        model = Recipes
        fields = (
            'author',
            'tags',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def get_filter_is_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def get_filter_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset
