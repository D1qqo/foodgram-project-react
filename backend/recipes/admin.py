from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientsInRecipe,
                     Recipe, ShoppingCart, Tag)


class FavouritesAdmin(admin.ModelAdmin):
    """Админка избранного."""
    list_display = ('recipe', 'user')


class IngredientAdmin(admin.ModelAdmin):
    """Админка ингредиентов."""
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


class IngredientsInRecipeAdmin(admin.ModelAdmin):
    """Админка связанной таблицы ингредиентов и рецептов."""
    list_display = ('recipe', 'ingredients', 'amount')


class RecipeAdmin(admin.ModelAdmin):
    """Админка рецептов."""
    list_display = ('name', 'author')
    list_filter = ('author', 'name', 'tags')
    readonly_fields = ('count_favorites',)

    def count_favorites(self, obj):
        return obj.favorites.count()


class ShoppingListAdmin(admin.ModelAdmin):
    """Админка списка покупок."""
    list_display = ('recipe', 'user')


class TagAdmin(admin.ModelAdmin):
    """Админка тегов."""
    list_display = ('name', 'color', 'slug')


admin.site.register(Favorite, FavouritesAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientsInRecipe, IngredientsInRecipeAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(ShoppingCart, ShoppingListAdmin)
admin.site.register(Tag, TagAdmin)
