from rest_framework.response import Response
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser import views

from .models import (User, Follow, Tag,
                     Ingredient, Recipe,
                     Favorite, ShoppingCart,
                     RecipeIngredients)
from .permissions import IsAuthorOrReadOnly
from .serializers import (TagSerializer, IngredientDetailSerializer,
                          RecipeSerializer, RecipeListSerializer,
                          CustomUserSerializer, SubscriptionListSerializer,
                          RecipeSerializerShort, RecipeCreateSerializer)


class TagViewset(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly
    ]


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientDetailSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly
    ]


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly
    ]

    def get_serializer_class(self):
        if self.action in ('list', 'retrive'):
            return RecipeListSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeCreateSerializer
        return RecipeSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        limit = self.request.query_params.get('limit')
        if limit:
            queryset = queryset[:int(limit)]
        return queryset

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(permissions.IsAuthenticated,)
    )
    def favorite(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            if not Favorite.objects.filter(
                user=user,
                recipe=recipe
            ).exists():
                Favorite.objects.create(user=request.user, recipe=recipe)
                recipes = Recipe.objects.filter(id=pk).first()
                serializer = RecipeSerializerShort(recipes)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {"errors": "Ошибка добавления в избранное."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        if request.method == 'DELETE':
            if Favorite.objects.filter(
                user=user,
                recipe=recipe
            ).exists():
                Favorite.objects.filter(user=user, recipe=recipe).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {"errors": "Ошибка. Нет записи в БД для удаления."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(permissions.IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            if not ShoppingCart.objects.filter(
                user=user,
                recipe=recipe
            ).exists():
                ShoppingCart.objects.create(user=request.user, recipe=recipe)
                recipes = Recipe.objects.filter(id=pk).first()
                serializer = RecipeSerializerShort(recipes)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {"errors": "Ошибка добавления в список покупок."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        if request.method == 'DELETE':
            if ShoppingCart.objects.filter(
                user=user,
                recipe=recipe
            ).exists():
                ShoppingCart.objects.filter(user=user, recipe=recipe).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {"errors": "Ошибка. Нет записи в БД для удаления."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(permissions.IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
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


class UserListViewSet(views.UserViewSet):
    serializer_class = CustomUserSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

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
        authors = User.objects.filter(following__user=request.user)
        serializer = SubscriptionListSerializer(
            authors, many=True, context={'request': request}
        )
        return Response(serializer.data)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscribe(self, request, id):
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
            else:
                return Response(
                    {"errors": "Ошибка подписки."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        if request.method == 'DELETE':
            if user != author and Follow.objects.filter(
                user=user,
                author=author
            ).exists():
                Follow.objects.filter(user=user, author=author).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {"errors": "Ошибка. Нет записи в БД для удаления."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_400_BAD_REQUEST)
