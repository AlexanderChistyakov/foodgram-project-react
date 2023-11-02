# Generated by Django 3.2.20 on 2023-11-02 08:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipeingredients',
            name='ingredient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredient_recipes', to='recipe.ingredient', verbose_name='Ингредиент'),
        ),
    ]
