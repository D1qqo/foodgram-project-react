from django.contrib import admin

from .models import (Ingredient, Tag, Recipe,
                     IngredientsInRecipe, Favourites, ShoppingList)


class IngredientAdmin(admin.ModelAdmin):
    """Класс админки ингредиентов."""
    list_display = ('title', 'unit_measurement')
    list_filter = ('title',)


class TagAdmin(admin.ModelAdmin):
    """Класс админки тегов."""
    list_display = ('title', 'color', 'slug')


class RecipeAdmin(admin.ModelAdmin):
    """Класс админки рецептов."""
    list_display = ('title', 'author')
    list_filter = ('author', 'title', 'tags')
    readonly_fields = ('count_favourites',)

    def count_favourites(self, obj):
        return obj.favourites.count()


class IngredientsInRecipeAdmin(admin.ModelAdmin):
    """Класс админки связанной таблицы ингредиентов и рецептов."""
    list_display = ('recipe', 'ingredient', 'amount')


class FavouritesAdmin(admin.ModelAdmin):
    """Класс админки избранного."""
    list_display = ('recipe', 'user')


class ShoppingListAdmin(admin.ModelAdmin):
    """Класс админки списка покупок."""
    list_display = ('recipe', 'user')


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(IngredientsInRecipe, IngredientsInRecipeAdmin)
admin.site.register(Favourites, FavouritesAdmin)
admin.site.register(ShoppingList, ShoppingListAdmin)
