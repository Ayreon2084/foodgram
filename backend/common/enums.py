from enum import Enum


class FileNames(Enum):
    TAGS = 'tags.json'
    INGREDIENTS = 'ingredients.json'


class IngredientFields(Enum):
    NAME = 'name'
    MEASUREMENT_UNIT = 'measurement_unit'


class TagFields(Enum):
    NAME = 'name'
    SLUG = 'slug'
