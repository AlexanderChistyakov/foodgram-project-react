from api.permissions import IsAuthorOrReadOnly
from api.serializers import (CustomUserSerializer, IngredientDetailSerializer,
                             RecipeCreateSerializer, RecipeSerializer,
                             RecipeSerializerShort, SubscriptionListSerializer,
                             TagSerializer)
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser import views
from recipe.models import (Favorite, Ingredient, Recipe, RecipeIngredients,
                           ShoppingCart, Tag)
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from user.models import Follow, User
from utils import views_utils


class UserListViewSet(views.UserViewSet):
    """Представление пользователей."""

    queryset = User.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('username', 'email')

    def get_queryset(self):
        queryset = super().get_queryset()
        limit = self.request.query_params.get('limit')
        if limit:
            queryset = queryset[:int(limit)]
        return queryset

    @action(
        detail=False,
        url_path='subscriptions',
        methods=('get',),
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscriptions(self, request):
        """Получение подписок и сериализация."""

        authors = User.objects.filter(following__user=request.user)
        serializer = SubscriptionListSerializer(
            authors, many=True, context={'request': request}
        )
        return Response(serializer.data)

    @action(
        detail=True,
        methods=('post', 'delete'),
        url_path='subscribe',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscribe(self, request, id):
        """Подписка на автора, отписка."""

        user = request.user
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            if user != author and not Follow.objects.filter(
                user=user,
                author=author
            ).exists():
                Follow.objects.create(user=request.user, author=author)
                follows = User.objects.filter(id=id).first()
                serializer = SubscriptionListSerializer(follows)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {'errors': 'Ошибка подписки.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if user != author and Follow.objects.filter(
            user=user,
            author=author
        ).exists():
            Follow.objects.filter(user=user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Ошибка. Нет записи в БД для удаления.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=False,
        url_path='me',
        methods=('get', 'patch'),
        permission_classes=(permissions.IsAuthenticated,)
    )
    def me(self, request):
        """Представление авторизованного пользователя."""

        if request.method == 'GET':
            serializer = CustomUserSerializer(
                request.user, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = self.get_serializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


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
