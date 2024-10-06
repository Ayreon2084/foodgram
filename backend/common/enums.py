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


class BooleanFields(Enum):
    TRUE = (True, 'True', 'true', '1', 1)
    FALSE = (False, 'False', 'false', '0', 0)

    @classmethod
    def is_true(cls, value):
        return value in cls.TRUE.value

    @classmethod
    def is_false(cls, value):
        return value in cls.FALSE.value


class RecipeRelatedFields(Enum):
    IS_FAVORITED = 'favorited_by'
    IS_IN_SHOPPING_CART = 'in_shopping_cart_of'
