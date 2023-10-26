from django.urls import path, include
from rest_framework.routers import SimpleRouter

from recipe.views import TagViewset, IngredientViewSet, RecipeViewSet
from user.views import UserListViewSet

app_name = 'api'

router = SimpleRouter()

router.register('tags', TagViewset)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)
router.register('users', UserListViewSet)


urlpatterns = [
    path('', include(router.urls)),

]
