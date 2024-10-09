import os
import random
import string

from django.utils.timezone import now

from common.enums import BooleanFields, IngredientFields
from recipes.models import IngredientRecipe


def generate_shopping_cart_content(user, shopping_cart_items):
    ingredient_totals = {}

    for item in shopping_cart_items:
        recipe = item.recipe
        for ingredient_recipe in recipe.ingredient_recipe.all():
            ingredient = ingredient_recipe.ingredient
            key = (ingredient.name, ingredient.measurement_unit)
            ingredient_totals[key] = (
                ingredient_totals.get(key, 0) + ingredient_recipe.amount
            )

    content_lines = [
        'Shopping List\n',
        f'Generated on: {now().strftime("%Y-%m-%d %H:%M:%S")}\n',
    ]

    for recipe in shopping_cart_items.values_list(
        'recipe__name', flat=True
    ).distinct():
        content_lines.append(f'\nRecipe: {recipe}')

    content_lines.append('\nIngredients:\n')
    for (name, unit), amount in ingredient_totals.items():
        content_lines.append(f'- {name} - {amount} {unit}\n')

    return '\n'.join(content_lines)


def delete_temp_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)


def generate_short_link(length=5):
    symbols = string.ascii_letters + string.digits
    return ''.join(random.choice(symbols) for _ in range(length))


def get_or_create_short_link(request, recipe):
    if recipe.short_link:
        return request.build_absolute_uri(f'/s/{recipe.short_link}')

    short_link = generate_short_link()
    recipe.short_link = short_link
    recipe.save()

    return request.build_absolute_uri(f'/s/{short_link}')


def filter_by_boolean(queryset, user, value, related_field, is_authenticated):
    if BooleanFields.is_true(value) and is_authenticated:
        return queryset.filter(**{f'{related_field}__user': user})
    if BooleanFields.is_false(value) and is_authenticated:
        return queryset.exclude(**{f'{related_field}__user': user})
    return queryset


def bulk_create_ingredients(recipe, ingredients):
    ingredient_instances = [
        IngredientRecipe(
            recipe=recipe,
            ingredient_id=ingredient[IngredientFields.ID.value],
            amount=ingredient[IngredientFields.AMOUNT.value]
        )
        for ingredient in ingredients
    ]
    IngredientRecipe.objects.bulk_create(ingredient_instances)
