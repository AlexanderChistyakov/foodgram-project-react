from django.urls import include, path
from recipe.views import IngredientViewSet, RecipeViewSet, TagViewset
from rest_framework.routers import SimpleRouter
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
