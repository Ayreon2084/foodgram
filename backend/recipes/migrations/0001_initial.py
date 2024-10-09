# Generated by Django 3.2.16 on 2024-10-07 18:02

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FavoriteRecipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'рецепт в избранном',
                'verbose_name_plural': 'Рецепты в избранном',
                'ordering': ('recipe',),
            },
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, verbose_name='Ингредиент')),
                ('measurement_unit', models.CharField(max_length=64, verbose_name='Ед. измерения')),
            ],
            options={
                'verbose_name': 'ингредиент',
                'verbose_name_plural': 'Ингредиенты',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='IngredientRecipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveSmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(32767)], verbose_name='Количество')),
            ],
            options={
                'verbose_name': 'ингредиент в рецепте',
                'verbose_name_plural': 'Ингредиенты в рецепте',
                'ordering': ('recipe', 'ingredient'),
                'default_related_name': 'ingredient_recipe',
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, verbose_name='Рецепт')),
                ('text', models.TextField(verbose_name='Описание рецепта')),
                ('image', models.ImageField(upload_to='recipes/', verbose_name='Изображение рецепта')),
                ('cooking_time', models.PositiveSmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(32767)], verbose_name='Время приготовления, мин.')),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации рецепта')),
                ('short_link', models.CharField(blank=True, max_length=10, null=True, unique=True, verbose_name='Сокращённая ссылка')),
            ],
            options={
                'verbose_name': 'рецепт',
                'verbose_name_plural': 'Рецепты',
                'ordering': ('-pub_date',),
                'default_related_name': 'recipes',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, verbose_name='Тег')),
                ('slug', models.SlugField(max_length=32, null=True, unique=True, validators=[django.core.validators.RegexValidator('^[-a-zA-Z0-9_]+$', message='Username must contain only alphanumeric characters in upper/lowercase, hyphens and underscores.')], verbose_name='Слаг')),
            ],
            options={
                'verbose_name': 'тег',
                'verbose_name_plural': 'Теги',
                'ordering': ('slug',),
            },
        ),
        migrations.CreateModel(
            name='ShoppingCart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='in_shopping_cart_of', to='recipes.recipe', verbose_name='Рецепт в корзине')),
            ],
            options={
                'verbose_name': 'корзина',
                'verbose_name_plural': 'Корзины',
                'ordering': ('recipe',),
            },
        ),
    ]
