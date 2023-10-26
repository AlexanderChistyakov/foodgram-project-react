from django.contrib import admin

from user.models import User, Follow
from recipe.models import Tag, Ingredient, Recipe, RecipeIngredients

admin.site.register(User)
admin.site.register(Follow)
admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(Recipe)
