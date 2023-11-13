import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from recipe.models import (
    Favorite, Ingredient, Recipe,
    RecipeIngredients, ShoppingCart, Tag
)
from user.models import Follow, User


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор создания пользователя."""

    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'username',
            'email',
            'password'
        )


class CustomUserSerializer(UserSerializer):
    """Сериализатор пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        """Проверка наличия подписки."""

        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=request.user,
            author=obj
        ).exists()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тега."""

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug'
        )


class IngredientIDAmountSerializer(serializers.ModelSerializer):
    """Сериализатор количества ингредиента с двумя полями - id и amount."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
    )

    class Meta:
        model = RecipeIngredients
        fields = (
            'id',
            'amount'
        )


class IngredientSerializer(IngredientIDAmountSerializer):
    """Сериализатор количества ингредиента для рецептов."""

    name = serializers.CharField(
        read_only=True,
        source='ingredient.name'
    )
    measurement_unit = serializers.CharField(
        read_only=True,
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredients
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class IngredientDetailSerializer(serializers.ModelSerializer):
    """Сериализатор одного ингредиента для страницы ингредиентов."""

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class Base64ImageField(serializers.ImageField):
    """Сериализатор для картинок."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(
                base64.b64decode(imgstr),
                name='temp.' + ext
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
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )


class RecipeListSerializer(RecipeSerializer):
    """Сериализатор для списка рецептов."""

    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_is_favorited(self, obj):
        """Проверка наличия рецепта в избранном."""

        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=request.user,
            recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        """Проверка наличия рецепта в корзине."""

        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user,
            recipe=obj
        ).exists()


class RecipeDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для одного рецепта после создания."""

    ingredients = IngredientIDAmountSerializer(
        many=True,
        source='recipe_ingredients'
    )
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта."""

    tags = serializers.ListField()
    ingredients = serializers.ListField()
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )
        read_only_fields = ('author',)
        # extra_kwargs = {
        #     'name': {'required': True},
        #     'text': {'required': True},
        #     'cooking_time': {'required': True},
        #     'image': {'required': True},
        #     'ingredients': {'required': True},
        #     'tags': {'required': True},
        # }

    def create_ingredients(self, ingredient_data, recipe):
        """Получение ингредиента, создание связи, возврат ингредиента."""

        ingredient = Ingredient.objects.get(pk=ingredient_data['id'])
        RecipeIngredients.objects.create(
            recipe=recipe,
            ingredient=ingredient,
            amount=ingredient_data['amount']
        )
        return ingredient

    def check_fields(self, validated_data):
        """Проверка полей."""

        fields = [
            'tags',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        ]
        check_fileds = []
        for key in validated_data.keys():
            check_fileds.append(key)
        if check_fileds != fields:
            raise serializers.ValidationError(
                'Все поля должны быть заполнены.'
            )

    def create(self, validated_data):
        """Создание рецепта."""

        # self.check_fields(validated_data)
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
            ingredient = self.create_ingredients(
                ingredient_data,
                recipe
            )
            ingredient_list.append(ingredient)
        recipe.tags.set(tags_list)
        recipe.ingredients.set(ingredient_list)
        return recipe

    def update(self, instance, validated_data):
        """Обновление рецепта."""

        # self.check_fields(validated_data)
        ingredient_list = []
        ingredients = validated_data.get('ingredients')
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )
        instance.image = validated_data.get('image', instance.image)
        instance.tags.set(validated_data.get('tags', instance.tags))
        for ingredient_data in ingredients:
            ingredient = self.create_ingredients(
                ingredient_data,
                instance
            )
            ingredient_list.append(ingredient)

        ingredient_list.append(ingredient)
        instance.ingredients.set(ingredient_list)
        instance.save()
        return instance

    def to_representation(self, instance):
        """Переопределение метода to_representation."""

        request = self.context.get('request')
        context = {'request': request}
        serializer = RecipeListSerializer(instance, context=context)
        data = serializer.data
        data['is_favorite'] = serializer.get_is_favorited(instance)
        data['is_in_shopping_cart'] = serializer.get_is_in_shopping_cart(
            instance
        )
        return data


class RecipeSerializerShort(serializers.ModelSerializer):
    """Короткий сериализатор рецепта."""

    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class SubscriptionListSerializer(CustomUserSerializer):
    """Сериализатор для подписок."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = CustomUserSerializer.Meta.fields + (
            'recipes', 'recipes_count'
        )

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
