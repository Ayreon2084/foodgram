from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from common.constants import LENGTH_32, LENGTH_64, LENGTH_128, LENGTH_256


User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Tag',
        max_length=LENGTH_32
    )
    slug = models.SlugField(
        verbose_name='Slug',
        max_length=LENGTH_32,
        null=True,
        unique=True,
        validators=[
            RegexValidator(
                r'^[-a-zA-Z0-9_]+$',
                message=(
                    'Username must contain only alphanumeric characters '
                    'in upper/lowercase, hyphens and underscores.'
                )
            )
        ],
    )

    class Meta:
        verbose_name = 'tag'
        verbose_name_plural = 'Tags'
        ordering = ('slug',)

    def __str__(self):
        return f'Tag {self.name} with slug {self.slug}'


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Ingredient',
        max_length=LENGTH_128
    )
    measurement_unit = models.CharField(
        verbose_name='Measurement unit',
        max_length=LENGTH_64,
    )

    class Meta:
        verbose_name = 'ingredient'
        verbose_name_plural = 'Ingredients'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit',),
                name='unique_ingredient'
            ),
        ]

    def __str__(self):
        return f'Ingredient {self.name}, {self.measurement_unit}.'


class IngredientRecipe(models.Model):
    recipe = models.ForeignKey(
        'Recipe',
        verbose_name='What recipes',
        on_delete=models.CASCADE,
        related_name='ingredient_recipe'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='What ingredient',
        on_delete=models.CASCADE,
        related_name='ingredient_recipe'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Quantity',
        default=1,
        validators=(MinValueValidator(1),)
    )

    class Meta:
        verbose_name = 'ingredient in recipe'
        verbose_name_plural = 'Ingredients in recipe'
        ordering = ('recipe', 'ingredient',)
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient',),
                name='unique_ingredients_in_recipe'
            ),
        ]

    def __str__(self):
        return (
            f'Recipe {self.recipe} requires '
            f'{self.amount} {self.ingredient.measurement_unit} '
            f'of {self.ingredient.name}'
        )


class Recipe(models.Model):
    name = models.CharField(
        verbose_name='Recipe',
        max_length=LENGTH_256
    )
    text = models.TextField(
        verbose_name='Recipe description'
    )
    image = models.ImageField(
        verbose_name='Meal picture',
        upload_to='recipes/'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Recipe author',
        related_name='recipes',
        on_delete=models.SET_NULL,
        null=True
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Cooking time in minutes',
        default=1,
        validators=(MinValueValidator(1),)
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through=IngredientRecipe,
        verbose_name='Ingredients in recipe',
        related_name='recipes',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Tags',
        related_name='recipes'
    )
    pub_date = models.DateTimeField(
        verbose_name='Publication date',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'recipe'
        verbose_name_plural = 'Recipes'
        ordering = ('-pub_date',)

    def __str__(self):
        f'Recipe {self.name} from author {self.author.username}.'
