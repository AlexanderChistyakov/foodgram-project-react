from django.contrib import admin

from .models import User, Follow, Tag, Ingredient, Recipe, RecipeIngredients

admin.site.register(User)
admin.site.register(Follow)
admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(Recipe)
admin.site.register(RecipeIngredients)