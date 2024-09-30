import random
import string

from common.enums import BooleanFields


def generate_short_link(length=5):
    symbols = string.ascii_letters + string.digits
    return ''.join(random.choice(symbols) for _ in range(length))


def filter_by_boolean(queryset, user, value, related_field, is_authenticated):
    """
    Utility function to filter or exclude based on boolean-like values.
    """
    if BooleanFields.is_true(value) and is_authenticated:
        return queryset.filter(**{f"{related_field}__user": user})
    elif BooleanFields.is_false(value) and is_authenticated:
        return queryset.exclude(**{f"{related_field}__user": user})
    return queryset