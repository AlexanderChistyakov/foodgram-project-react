from django.contrib import admin
from recipe.models import (Favorite, Ingredient, Recipe, RecipeIngredients,
                           ShoppingCart, Tag)

admin.site.register(Tag)
admin.site.register(ShoppingCart)
admin.site.register(RecipeIngredients)


class FavoriteInstanceInline(admin.TabularInline):
    model = Favorite


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'display_tags', 'get_favorites_count',)
    list_filter = ('author', 'name', 'tags')
    fields = (
        'name', 'author', 'tags',
        'ingredients', 'image', 'text',
        'cooking_time',
    )
    inlines = (FavoriteInstanceInline,)

    def display_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])

    display_tags.short_description = 'Теги'

    @admin.display(description='В избранном')
    def get_favorites_count(self, obj):
        return obj.favorites.count()


admin.site.register(Recipe, RecipeAdmin)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


admin.site.register(Ingredient, IngredientAdmin)
