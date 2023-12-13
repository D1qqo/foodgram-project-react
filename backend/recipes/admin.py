from django.contrib import admin

from .models import (Favourites, Ingredient, IngredientsInRecipe,
                     Recipe, ShoppingList, Tag)


class IngredientAdmin(admin.ModelAdmin):
    """Админка ингредиентов."""
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


class TagAdmin(admin.ModelAdmin):
    """Админка тегов."""
    list_display = ('title', 'color', 'slug')


class RecipeAdmin(admin.ModelAdmin):
    """Админка рецептов."""
    list_display = ('title', 'author')
    list_filter = ('author', 'title', 'tags')
    readonly_fields = ('count_favourites',)

    def count_favourites(self, obj):
        return obj.favourites.count()


class IngredientsInRecipeAdmin(admin.ModelAdmin):
    """Админка связанной таблицы ингредиентов и рецептов."""
    list_display = ('recipe', 'ingredient', 'amount')


class FavouritesAdmin(admin.ModelAdmin):
    """Админка избранного."""
    list_display = ('recipe', 'user')


class ShoppingListAdmin(admin.ModelAdmin):
    """Админка списка покупок."""
    list_display = ('recipe', 'user')


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(IngredientsInRecipe, IngredientsInRecipeAdmin)
admin.site.register(Favourites, FavouritesAdmin)
admin.site.register(ShoppingList, ShoppingListAdmin)
