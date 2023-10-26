from django.conf import settings
from django.db import models
from django.core.validators import RegexValidator, MinValueValidator


class Tag(models.Model):
    """Модель тега."""
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
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиента."""
    name = models.CharField(
        max_length=150,
        unique=True,
        blank=False,
        verbose_name='Название ингредиента',
    )
    measurement_unit = models.CharField(
        max_length=200,
        blank=False,
        verbose_name='Название меры',
    )

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient',
            )
        ]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта."""
    name = models.CharField(
        max_length=150,
        unique=True,
        blank=False,
        verbose_name='Название рецепта',
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
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
        upload_to='media/images/',
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
        verbose_name='Время приготовления в минутах',
    )
    pub_date = models.DateTimeField(
        'Дата публикации рецепта',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class RecipeIngredients(models.Model):
    """Модель связи рецепта и ингредиента."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_recipes',
        verbose_name='Ингридиент',
    )
    amount = models.PositiveIntegerField(
        blank=False,
        verbose_name='Количество',
        validators=[MinValueValidator(1, 'Не меньше 1.')]
    )

    class Meta:
        verbose_name = 'Мера(таблица m2m рецепт-ингредиент)'
        verbose_name_plural = 'Мера(таблица m2m рецепт-ингредиент)'


class Favorite(models.Model):
    """Модель избранного."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites'
    )


class ShoppingCart(models.Model):
    """Модель корзины."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart'
    )
