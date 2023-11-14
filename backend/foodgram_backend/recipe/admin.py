from django import forms
from django.contrib import admin

from import_export import resources
from import_export.admin import ImportExportModelAdmin

from recipe.models import (
    Favorite, Ingredient, Recipe,
    RecipeIngredients, ShoppingCart, Tag
)

admin.site.register(ShoppingCart)
admin.site.register(RecipeIngredients)


class FavoriteInstanceInline(admin.TabularInline):
    model = Favorite


class AmountInline(admin.TabularInline):
    model = RecipeIngredients
    min_num = 1
    autocomplete_fields = ('ingredient',)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'display_tags', 'get_favorites_count',)
    list_filter = ('author', 'name', 'tags')
    fields = (
        'name',
        'author',
        'tags',
        'image',
        'text',
        'cooking_time',
    )
    search_fields = ('name', 'tags__name', 'author__username')
    inlines = (AmountInline, FavoriteInstanceInline)

    def display_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])

    display_tags.short_description = 'Теги'

    @admin.display(description='В избранном')
    def get_favorites_count(self, obj):
        return obj.favorites.count()


admin.site.register(Recipe, RecipeAdmin)


class IngredientResource(resources.ModelResource):

    class Meta:
        model = Ingredient
        # fields = (
        #     'name',
        #     'measurement_unit',
        # )
        import_id_fields = ('name', 'measurement_unit')
        delimiter = ','
        exclude = ('id',)


class IngredientAdmin(ImportExportModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)
    resource_classes = (IngredientResource,)


admin.site.register(Ingredient, IngredientAdmin)


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = '__all__'

    def clean_color(self):
        """Проверка на уникальность цвета."""

        if Tag.objects.filter(
            color=self.cleaned_data['color'].upper()
        ).exists():
            raise forms.ValidationError('Такой цвет уже существует')
        return self.cleaned_data['color'].upper()


class TagAdmin(admin.ModelAdmin):
    form = TagForm


admin.site.register(Tag, TagAdmin)
