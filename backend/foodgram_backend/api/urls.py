from django.urls import path, include
from rest_framework.routers import SimpleRouter
from . import views

app_name = 'api'

router = SimpleRouter()

router.register('tags', views.TagViewset)
router.register('ingredients', views.IngredientViewSet)
router.register('recipes', views.RecipeViewSet)
router.register('users', views.UserListViewSet)
# router.register('users/subscriptions', views.SubscriptionListSerializer)

urlpatterns = [
    path('users/<int:id>/subscribe/', views.subscribe, name='subscribe'),
    path('', include(router.urls)),

]
