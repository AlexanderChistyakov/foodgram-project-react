import base64

from django.core.files.base import ContentFile
from rest_framework import serializers

from recipe.models import (Favorite, Ingredient, Recipe, RecipeIngredients,
                           ShoppingCart, Tag)
from user.models import Follow
from user.serializers import CustomUserSerializer


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тега."""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        pagination_class = None


class IngredientDetailSerializer(serializers.ModelSerializer):
    """Сериализатор одного ингредиента."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        pagination_class = None


class IngredientAmountSerializer(serializers.ModelSerializer):
    """Сериализатор количества ингредиента."""
    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount')
        pagination_class = None

    def get_ingredient(self, obj):
        """Получение ингредиента по id для следующих методов."""
        return Ingredient.objects.filter(name=obj).first()

    def get_id(self, obj):
        """Получение id ингредиента."""
        ingredient = self.get_ingredient(obj)
        return ingredient.id

    def get_name(self, obj):
        """Получение названия ингредиента."""
        ingredient = self.get_ingredient(obj)
        return ingredient.name

    def get_measurement_unit(self, obj):
        """Получение единицы измерения ингредиента."""
        ingredient = self.get_ingredient(obj)
        return ingredient.measurement_unit

    def get_amount(self, obj):
        """Получение количества ингредиента."""
        ingredient = self.get_ingredient(obj)
        recipe_ingredient = RecipeIngredients.objects.filter(
            ingredient_id=ingredient.id
        ).first()
        return recipe_ingredient.amount


class IngredientAmountSerializerForNewRecipe(serializers.ModelSerializer):
    """Сериализатор количества ингредиента."""
    id = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()

    class Meta:
        model = RecipeIngredients
        fields = ('id',  'amount')
        pagination_class = None

    def get_ingredient(self, obj):
        """Получение ингредиента по id для следующих методов."""
        return Ingredient.objects.filter(name=obj).first()

    def get_id(self, obj):
        """Получение id ингредиента."""
        ingredient = self.get_ingredient(obj)
        return ingredient.id

    def get_amount(self, obj):
        """Получение количества ингредиента."""
        ingredient = self.get_ingredient(obj)
        recipe_ingredient = RecipeIngredients.objects.filter(
            ingredient_id=ingredient.id
        ).first()
        return recipe_ingredient.amount


class Base64ImageField(serializers.ImageField):
    """Сериализатор для картинок."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class RecipeListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка рецептов."""
    ingredients = IngredientAmountSerializer(many=True)
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )
        pagination_class = None

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


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для одного рецепта."""
    tags = TagSerializer(many=True)
    ingredients = IngredientAmountSerializer(many=True)
    author = CustomUserSerializer()
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time'
        )


class RecipeDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для одного рецепта после создания."""
    ingredients = IngredientAmountSerializerForNewRecipe(many=True)
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image',
            'name',  'text', 'cooking_time'
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
        extra_kwargs = {
            'name': {'required': True},
            'text': {'required': True},
            'cooking_time': {'required': True},
            'image': {'required': True},
            'ingredients': {'required': True},
            'tags': {'required': True},
        }

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


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для корзины."""
    ingredient = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()

    class Meta:
        model = ShoppingCart
        fields = ('ingredient', 'amount')

    def get_ingredient(self, obj):
        """Получение ингредиента."""
        return obj.recipe.ingredients.all().first()

    def get_amount(self, obj):
        """Получение количества."""
        return obj.recipe.recipe_ingredients.all().first().amount
