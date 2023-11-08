from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api.views import (
    IngredientViewSet, RecipeViewSet, TagViewset, UserListViewSet
)

app_name = 'api'

router = SimpleRouter()

router.register('tags', TagViewset)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)
router.register('users', UserListViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
