from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from .models import (User, Follow, Tag,
                     Ingredient, Recipe,
                     RecipeIngredients, Favorite)


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name',
                  'username', 'email', 'password')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'username': {'required': True},
            'email': {'required': True},
            'password': {'required': True}
        }


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id',
            'username', 'first_name',
            'last_name', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Follow.objects.filter(
                user=request.user, author=obj
            ).exists()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        pagination_class = None


class IngredientDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        pagination_class = None


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount')
        pagination_class = None

    def get_ingredient(self, obj):
        return Ingredient.objects.filter(name=obj).first()

    def get_id(self, obj):
        ingredient = self.get_ingredient(obj)
        return ingredient.id

    def get_name(self, obj):
        ingredient = self.get_ingredient(obj)
        return ingredient.name

    def get_measurement_unit(self, obj):
        ingredient = self.get_ingredient(obj)
        return ingredient.measurement_unit

    def get_amount(self, obj):
        ingredient = self.get_ingredient(obj)
        recipe_ingredient = RecipeIngredients.objects.filter(
            ingredient_id=ingredient.id
        ).first()
        return recipe_ingredient.amount


class RecipeListSerializer(serializers.ModelSerializer):
    ingredients = IngredientAmountSerializer(many=True)
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer()
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'name', 'image', 'text', 'cooking_time'
        )
        pagination_class = None

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=request.user, recipe=obj
        ).exists()


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = IngredientAmountSerializer(many=True)
    author = CustomUserSerializer()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time'
        )


class RecipeSerializerShort(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'cooking_time'
        )


class SubscriptionListSerializer(serializers.ModelSerializer):
    email = serializers.PrimaryKeyRelatedField(read_only=True)
    id = serializers.PrimaryKeyRelatedField(read_only=True)
    username = serializers.PrimaryKeyRelatedField(read_only=True)
    first_name = serializers.PrimaryKeyRelatedField(read_only=True)
    last_name = serializers.PrimaryKeyRelatedField(read_only=True)
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and not request.user.is_anonymous:
            return Follow.objects.filter(
                user=request.user, author=obj
            ).exists()
        return False

    def get_recipes(self, obj):
        queryset = Recipe.objects.filter(author=obj)
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            queryset = queryset[:int(recipes_limit)]
        return RecipeSerializerShort(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author_id=obj.id).count()
