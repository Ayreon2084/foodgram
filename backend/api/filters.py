import django_filters

from common.enums import RecipeRelatedFields
from recipes.models import Recipe
from .utils import filter_by_boolean


class RecipeFilter(django_filters.FilterSet):
    author = django_filters.NumberFilter(field_name="author__id")
    tags = django_filters.AllValuesMultipleFilter(field_name="tags__slug")
    is_favorited = django_filters.CharFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = django_filters.CharFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']

    def filter_is_favorited(self, queryset, name, value):
        return filter_by_boolean(
            queryset,
            self.request.user,
            value,
            RecipeRelatedFields.IS_FAVORITED.value,
            self.request.user.is_authenticated
        )

    def filter_is_in_shopping_cart(self, queryset, name, value):
        return filter_by_boolean(
            queryset,
            self.request.user,
            value,
            RecipeRelatedFields.IS_IN_SHOPPING_CART.value,
            self.request.user.is_authenticated
        )
