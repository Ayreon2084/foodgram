from django.contrib.auth import get_user_model
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models

from common.constants import (LENGTH_32, LENGTH_64, LENGTH_128, LENGTH_256,
                              MAX_VALUE, MIN_VALUE, SLUG_REGEX)

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Тег',
        max_length=LENGTH_32
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        max_length=LENGTH_32,
        null=True,
        unique=True,
        validators=[
            RegexValidator(
                SLUG_REGEX,
                message=(
                    'Username must contain only alphanumeric characters '
                    'in upper/lowercase, hyphens and underscores.'
                ),
            )
        ]
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'
        ordering = ('slug',)

    def __str__(self):
        return f'Тег "{self.name}" со слагом "{self.slug}"'


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Ингредиент',
        max_length=LENGTH_128
    )
    measurement_unit = models.CharField(
        verbose_name='Ед. измерения',
        max_length=LENGTH_64
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit',),
                name='unique_ingredient'
            ),
        ]

    def __str__(self):
        return (
            f'Ингредиент "{self.name}", '
            f'ед. измерения "{self.measurement_unit}".'
        )


class IngredientRecipe(models.Model):
    recipe = models.ForeignKey(
        'Recipe',
        verbose_name='Рецепт',
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        default=MIN_VALUE,
        validators=(
            MinValueValidator(MIN_VALUE),
            MaxValueValidator(MAX_VALUE)
        )
    )

    class Meta:
        verbose_name = 'ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        ordering = ('recipe', 'ingredient',)
        default_related_name = 'ingredient_recipe'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient',),
                name='unique_ingredients_in_recipe'
            ),
        ]

    def __str__(self):
        return (
            f'Рецепт "{self.recipe}" требует наличия '
            f'"{self.amount}" "{self.ingredient.measurement_unit}" '
            f'"{self.ingredient.name}"'
        )


class Recipe(models.Model):
    name = models.CharField(
        verbose_name='Рецепт',
        max_length=LENGTH_256
    )
    text = models.TextField(
        verbose_name='Описание рецепта'
    )
    image = models.ImageField(
        verbose_name='Изображение рецепта',
        upload_to='recipes/'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        on_delete=models.SET_NULL,
        null=True
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления, мин.',
        default=MIN_VALUE,
        validators=(
            MinValueValidator(MIN_VALUE),
            MaxValueValidator(MAX_VALUE)
        )
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through=IngredientRecipe,
        verbose_name='Ингредиент в рецепте',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации рецепта',
        auto_now_add=True
    )
    short_link = models.CharField(
        verbose_name='Сокращённая ссылка',
        max_length=10,
        unique=True,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)
        default_related_name = 'recipes'

    def __str__(self):
        return f'Рецепт "{self.name}" от автора: "{self.author.username}".'


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Кто добавил рецепт в избранное',
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт в избранном',
        on_delete=models.CASCADE,
        related_name='favorited_by'
    )

    class Meta:
        verbose_name = 'рецепт в избранном'
        verbose_name_plural = 'Рецепты в избранном'
        ordering = ('recipe',)
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe',),
                name='unique_favorite_recipe',
            ),
        ]

    def __str__(self):
        return (
            f'Пользователь "{self.user}" добавил '
            f'рецепт "{self.recipe}" '
            f'в избранное.'
        )


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Чья корзина',
        on_delete=models.CASCADE,
        related_name='shopping_cart'
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт в корзине',
        on_delete=models.CASCADE,
        related_name='in_shopping_cart_of'
    )

    class Meta:
        verbose_name = 'корзина'
        verbose_name_plural = 'Корзины'
        ordering = ('recipe',)
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe',),
                name='unique_shopping_cart',
            ),
        ]

    def __str__(self):
        return (
            f'Пользователь "{self.user}" добавил '
            f'рецепт "{self.recipe}" '
            'в корзинуА.'
        )
