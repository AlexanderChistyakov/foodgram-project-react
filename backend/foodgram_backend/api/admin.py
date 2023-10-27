from django.contrib import admin
from user.models import User, Follow
from recipe.models import Tag, Ingredient, Recipe

admin.site.register(User)
admin.site.register(Follow)
admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(Recipe)


class UserFilter(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('username', 'email')


admin.site.unregister(User)
admin.site.register(User, UserFilter)


class RecipeFilter(admin.ModelAdmin):
    list_display = ('name', 'author', 'tags',
                    'ingredients', 'image',
                    'cooking_time', 'pub_date')
    list_filter = ('author', 'name', 'tags')

admin.site.unregister(Recipe)
admin.site.register(Recipe, RecipeFilter)