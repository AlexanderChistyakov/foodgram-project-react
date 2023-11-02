import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipe.models import (Favorite, Ingredient, Recipe, RecipeIngredients,
                           ShoppingCart, Tag)
from rest_framework import serializers
from user.models import Follow, User


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор создания пользователя."""

    class Meta:
        model = User
        fields = (
            'id', 'first_name', 'last_name', 'username', 'email', 'password'
        )


class CustomUserSerializer(UserSerializer):
    """Сериализатор пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id',
            'username', 'first_name',
            'last_name', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        """Проверка наличия подписки."""

        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=request.user, author=obj
        ).exists()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тега."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientIDAmountSerializer(serializers.ModelSerializer):
    """Сериализатор количества ингредиента с двумя полями -
    id и amount."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
    )

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'amount')


class IngredientSerializer(IngredientIDAmountSerializer):
    """Сериализатор количества ингредиента для рецептов."""

    name = serializers.CharField(read_only=True,
                                 source='ingredient.name')
    measurement_unit = serializers.CharField(
        read_only=True,
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientDetailSerializer(serializers.ModelSerializer):
    """Сериализатор одного ингредиента для страницы ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class Base64ImageField(serializers.ImageField):
    """Сериализатор для картинок."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(
                base64.b64decode(imgstr), name='temp.' + ext
            )
        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для одного рецепта."""

    tags = TagSerializer(many=True)
    ingredients = IngredientSerializer(
        many=True,
        source='recipe_ingredients'
    )
    author = CustomUserSerializer()
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time'
        )


class RecipeListSerializer(RecipeSerializer):
    """Сериализатор для списка рецептов."""

    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        """Проверка наличия рецепта в избранном."""

        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=request.user, recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        """Проверка наличия рецепта в корзине."""

        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe=obj
        ).exists()


class RecipeDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для одного рецепта после создания."""

    ingredients = IngredientIDAmountSerializer(
        many=True, source='recipe_ingredients'
    )
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image',
            'name', 'text', 'cooking_time'
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта."""

    tags = serializers.ListField(
        child=serializers.IntegerField(min_value=0)
    )
    ingredients = serializers.ListField()
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time'
        )
        read_only_fields = ('author',)

    def create(self, validated_data):
        """Создание рецепта."""

        tags_list = []
        ingredient_list = []
        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        for id in tags:
            if id:
                tag = Tag.objects.get(id=id)
                tags_list.append(tag)
        for ingredient_data in ingredients:
            ingredient = Ingredient.objects.get(pk=ingredient_data['id'])
            RecipeIngredients.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=ingredient_data['amount']
            )
            ingredient_list.append(ingredient)
        recipe.tags.set(tags_list)
        recipe.ingredients.set(ingredient_list)
        return recipe

    def update(self, instance, validated_data):
        """Обновление рецепта."""

        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeDetailSerializer(instance, context=context).data


class RecipeSerializerShort(serializers.ModelSerializer):
    """Короткий сериализатор рецепта."""

    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionListSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок."""

    email = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user'
    )
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'recipes', 'recipes_count'
        )

    def to_representation(self, instance):
        """Переопределение метода to_representation для возвращения полей
        по первичному ключу."""

        return {
            'email': instance.email,
            'id': instance.id,
            'username': instance.username,
            'first_name': instance.first_name,
            'last_name': instance.last_name,
        }

    def get_is_subscribed(self, obj):
        """Проверка наличия подписки."""

        request = self.context.get('request')
        if request and not request.user.is_anonymous:
            return Follow.objects.filter(
                user=request.user, author=obj
            ).exists()
        return False

    def get_recipes(self, obj):
        """Получение рецептов."""

        queryset = Recipe.objects.filter(author=obj)
        request = self.context.get('request')
        if request:
            recipes_limit = request.query_params.get('recipes_limit')
            if recipes_limit:
                queryset = queryset[:int(recipes_limit)]
        return RecipeSerializerShort(queryset, many=True).data

    def get_recipes_count(self, obj):
        """Получение количества рецептов."""

        return Recipe.objects.filter(author_id=obj.id).count()
