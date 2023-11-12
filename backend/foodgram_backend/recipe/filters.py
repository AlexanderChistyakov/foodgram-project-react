from django_filters.rest_framework import FilterSet, filters

from recipe.models import Ingredient, Recipe, Tag


class RecipeFilter(FilterSet):
    """Фильтр рецептов."""

    author = filters.CharFilter(
        field_name='author__id',
    )
    tags = filters.ModelMultipleChoiceFilter(
        # method='filter_tags',
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_favorited = filters.NumberFilter(
        method='filter_is_favorited',
    )
    is_in_shopping_cart = filters.NumberFilter(
        method='filter_is_in_shopping_cart',
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, _, value):
        """Проверка наличия рецепта в избранном пользователя."""

        if not self.request.user.is_authenticated:
            return queryset.none()
        if value and self.request.user.is_authenticated:
            return queryset.filter(
                favorites__user=self.request.user
            )
        return queryset

    def filter_is_in_shopping_cart(self, queryset, _, value):
        """Проверка наличия рецепта в списке покупок пользователя."""

        if not self.request.user.is_authenticated:
            return queryset.none()
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset

    def filter_tags(self, queryset, _, value):
        """Фильтр по тегам."""

        if not value or (not queryset.filter(tags__in=value).exists()):
            return queryset.none()
        if value:
            return queryset.filter(tags__in=value)
        return queryset


class IngredientFilter(FilterSet):
    """Фильтр ингредиентов."""

    name = filters.CharFilter(
        field_name='name',
        lookup_expr='icontains'
    )

    class Meta:
        model = Ingredient
        fields = ('name',)


class TagFilter(FilterSet):

    class Meta:
        model = Tag
        fields = ('name', 'slug')
