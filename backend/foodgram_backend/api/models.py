from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


class User(AbstractUser):
    email = models.EmailField(unique=True,
                              verbose_name='Email')
    username = models.CharField(max_length=150,
                                unique=True,
                                verbose_name='Юзернейм',
                                null=False,
                                blank=False,
                                validators=[RegexValidator(
                                    regex=r'^[\w.@+-]+\Z',
                                )])
    first_name = models.CharField(max_length=150,
                                  verbose_name='Имя',
                                  null=False,
                                  blank=False)
    last_name = models.CharField(max_length=150,
                                 verbose_name='Фамилия',
                                 null=False,
                                 blank=False)


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_author'
            )
        ]


class Tag(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        blank=False,
        verbose_name='Название тега'
    )
    color = models.CharField(
        max_length=7,
        blank=False,
        verbose_name='Цвет тега',
        validators=[
            RegexValidator(
                regex=r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
            )
        ]
    )
    slug = models.SlugField(
        unique=True,
        blank=False,
        verbose_name='Слаг тега',
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=150,
        unique=True,
        blank=False,
        verbose_name='Название ингредиента',
    )
    measurement_unit = models.CharField(
        max_length=10,
        blank=False,
        verbose_name='Название меры',
    )

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(
        max_length=150,
        unique=True,
        blank=False,
        verbose_name='Название рецепта',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        blank=True,
        verbose_name='Теги',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        blank=True,
        verbose_name='Ингредиенты',
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipes/images/',
        default='api/default_recipe.jpg',
        help_text='Загрузка картинки к рецепту',
    )
    text = models.TextField(
        blank=True,
        verbose_name='Описание рецепта',
    )
    cooking_time = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='Время приготовления',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredients(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
    )
    amount = models.PositiveIntegerField(
        blank=False,
        verbose_name='Количество',
    )

    class Meta:
        verbose_name = 'Мера(таблица m2m рецепт-ингредиент)'
        verbose_name_plural = 'Мера(таблица m2m рецепт-ингредиент)'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites'
    )


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart'
    )
