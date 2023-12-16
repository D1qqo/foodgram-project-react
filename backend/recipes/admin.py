from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet

from .models import (
    Favourite,
    Ingredient,
    IngredientsInRecipe,
    Recipe,
    ShoppingList,
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
        'description',
        'author',
        'cooking_time',
        'pub_date',
        'in_favourites',
    )
    list_editable = ('name', 'description')
    search_fields = ('name', 'author__username')
    list_filter = ('author', 'name', 'tags',)
    inlines = (IngredientRecipeInLine,)

    def in_favourites(self, obj):
        return obj.favourites.count()


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    list_editable = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name', 'measurement_unit')


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')
    list_editable = ('name', 'color', 'slug')
    search_fields = ('name', 'slug')


class FavouriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    list_editable = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')


class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    list_editable = ('user', 'recipe')
    list_filter = ('recipe',)
    search_fields = ('user__username', 'recipe__name')


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Favourite, FavouriteAdmin)
admin.site.register(ShoppingList, ShoppingListAdmin)
