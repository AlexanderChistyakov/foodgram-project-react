from api.permissions import IsAuthorOrReadOnly
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from recipe.models import (Favorite, Ingredient, Recipe, RecipeIngredients,
                           ShoppingCart, Tag)
from recipe.serializers import (
    IngredientDetailSerializer, RecipeCreateSerializer, RecipeSerializer,
    RecipeSerializerShort, TagSerializer
)
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from utils import views_utils


class TagViewset(viewsets.ReadOnlyModelViewSet):
    """Представление тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def list(self, _):
        """Получение тегов в виде списка словарей (значение 'result').
        Функция изменяет вывод тегов, т.к. из-за настроек проекта без данного
        метода получаем  результат с пагинацией."""
        return views_utils.list(self, _)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientDetailSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

    def list(self, _):
        """Получение ингредиентов в виде списка словарей (значение 'result').
        Функция изменяет вывод тегов, т.к. из-за настроек проекта без данного
        метода получаем  результат с пагинацией."""

        return views_utils.list(self, _)


class RecipeViewSet(viewsets.ModelViewSet):
    """Представление рецептов."""

    queryset = Recipe.objects.all()
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly
    )

    def get_serializer_class(self):
        """Выбор сериализатора рецептов."""

        if self.action in ('create', 'update', 'partial_update'):
            return RecipeCreateSerializer
        return RecipeSerializer

    def get_queryset(self):
        """Получение кверисета."""

        queryset = super().get_queryset()
        limit = self.request.query_params.get('limit')
        if limit:
            queryset = queryset[:int(limit)]
        if self.request.query_params.get('author'):
            queryset = queryset.filter(
                author=self.request.query_params.get('author')
            )
        if self.request.query_params.get('is_in_shopping_cart') == '1':
            queryset = queryset.filter(
                shopping_cart__user=self.request.user
            )
        if self.request.query_params.get('is_in_shopping_cart') == '0':
            queryset = queryset.filter(shopping_cart__isnull=True)
        if self.request.query_params.get('tags'):
            queryset = queryset.filter(
                tags__slug=self.request.query_params.get('tags')
            )
        if self.request.query_params.get('is_favorited') == '1':
            queryset = queryset.filter(
                favorites__user=self.request.user
            )
        if self.request.query_params.get('is_favorited') == '0':
            queryset = queryset.filter(favorites__isnull=True)
        return queryset

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(permissions.IsAuthenticated,)
    )
    def favorite(self, request, pk):
        """Добавление рецепта в избранное, удаление из избранного."""

        return views_utils.favorite(
            self, request, pk, Favorite, Recipe, RecipeSerializerShort
        )

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(permissions.IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        """Добавление рецепта в список покупок, удаление из списка покупок."""

        return views_utils.favorite(
            self, request, pk, ShoppingCart, Recipe, RecipeSerializerShort
        )

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(permissions.IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """Скачивание txt-файла со списком покупок."""

        shopping_cart = ShoppingCart.objects.filter(
            user=request.user
        ).values_list('recipe_id', flat=True)

        ingredients = RecipeIngredients.objects.filter(
            recipe_id__in=shopping_cart
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount')).order_by('ingredient__name')

        shopping_list_content = []

        for ingredient in ingredients:
            shopping_list_content.append(
                f'{ingredient["ingredient__name"]}:'
                + f' {ingredient["ingredient__measurement_unit"]},'
                + f' {ingredient["amount"]}\n'
            )

        shopping_list_string = ''.join(shopping_list_content)
        filename = 'shopping_list.txt'

        response = HttpResponse(
            shopping_list_string, content_type='text/plain'
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
