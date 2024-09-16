# from django.contrib.auth import get_user_model
# from django.core.validators import MinValueValidator
# from django.db import models

# from common.constants import LENGTH_64, LENGTH_128, LENGTH_256


# User = get_user_model()


# class Tag(models.Model):
#     ...


# class Ingredient(models.Model):
#     name = models.CharField(
#         verbose_name='Ingredient',
#         max_length=LENGTH_128
#     )
#     measurement_unit = models.CharField(
#         verbose_name='Measurement unit',
#         max_length=LENGTH_64
#     )


# class IngredientRecipe(models.Model):
#     ...


# class Recipe(models.Model):
#     name = models.CharField(
#         verbose_name='Recipe',
#         max_length=LENGTH_256
#     )
#     text = models.TextField(
#         verbose_name='Recipe description'
#     )
#     image = models.ImageField(
#         verbose_name='Meal picture'
#         upload_to='recipes/'
#     )
#     author = models.ForeignKey(
#         User,
#         verbose_name='Recipe author',
#         related_name='recipes',
#         on_delete=models.CASCADE,
#     )
#     cooking_time = models.PositiveSmallIntegerField(
#         verbose_name='Cooking time in minutes'
#         validators=MinValueValidator(1)
#     )
#     ingredients = models.ManyToManyField(
#         IngredientRecipe,
#         verbose_name='Ingredients in recipe',
#         related_name='recipes'
#     )
#     tags = models.ManyToManyField(
#         Tag,
#         verbose_name='Tags'
#         related_name='recipes'
#     )






