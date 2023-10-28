from django.contrib import admin

from user.models import User, Follow
from recipe.models import Tag, Ingredient, Recipe, Favorite

admin.site.register(Follow)
admin.site.register(Tag)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('username', 'email')


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


class FavoriteInstanceInline(admin.TabularInline):
    model = Favorite


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'display_tags', 'get_favorites_count',)
    list_filter = ('author', 'name', 'tags')
    fields = ('name', 'author', 'tags',
              'ingredients', 'image', 'text',
              'cooking_time', )
    inlines = [FavoriteInstanceInline]

    def display_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])

    display_tags.short_description = 'Теги'

    @admin.display(description='В избранном')
    def get_favorites_count(self, obj):
        return obj.favorites.count()


admin.site.unregister(Recipe)
admin.site.register(Recipe, RecipeAdmin)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


admin.site.unregister(Ingredient)
admin.site.register(Ingredient, IngredientAdmin)
