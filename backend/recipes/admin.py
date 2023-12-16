from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet

from recipes.models import (
    Favorite,
    Ingredient,
    IngredientsInRecipe,
    Recipes,
    ShoppingCart,
    Tag,
)


class IngredientRecipeForm(BaseInlineFormSet):

    def clean(self):
        super(IngredientRecipeForm, self).clean()
        for form in self.forms:
            if not hasattr(form, 'cleaned_data'):
                continue
            data = form.cleaned_data
            if data.get('DELETE'):
                raise ValidationError(
                    'Нельзя удалять все ингредиенты из рецепта даже в админке!'
                )


class IngredientRecipeInLine(admin.TabularInline):
    model = IngredientsInRecipe
    min_num = 1
    formset = IngredientRecipeForm


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'text',
        'author',
        'cooking_time',
        'pub_date',
        'in_favorites',
    )
    list_editable = ('name', 'text')
    search_fields = ('name', 'author__username')
    list_filter = ('author', 'name', 'tags',)
    inlines = (IngredientRecipeInLine,)

    def in_favorites(self, obj):
        return obj.favorites.count()


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    list_editable = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name', 'measurement_unit')


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')
    list_editable = ('name', 'color', 'slug')
    search_fields = ('name', 'slug')


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    list_editable = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')


class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    list_editable = ('user', 'recipe')
    list_filter = ('recipe',)
    search_fields = ('user__username', 'recipe__name')


admin.site.register(Recipes, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingListAdmin)
