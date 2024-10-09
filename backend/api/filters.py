import operator
from functools import reduce

import django_filters
from django.db import models
from rest_framework import filters

from common.enums import RecipeRelatedFields
from recipes.models import Recipe, Tag
from .utils import filter_by_boolean


class RecipeFilter(django_filters.FilterSet):
    """
    FilterSet for filtering recipes based on the following criterias.

    - by author,
    - by tags,
    - whether they are favorited by user,
    - whether they are in the user's shopping cart.
    """

    author = django_filters.NumberFilter(field_name='author__id')
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
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
        """
        Filter the queryset to include only recipes favorited by the user.

        Args:
            queryset (QuerySet): The initial queryset of recipes.
            name (str): The name of the filter.
            value (str): The filter value, expected to be '1' or '0',
                         but boolean, str ('True'/'False') and integers 1 and 0
                         are also accepted.

        Returns:
            QuerySet: The filtered queryset containing only favorited recipes.
        """
        return filter_by_boolean(
            queryset,
            self.request.user,
            value,
            RecipeRelatedFields.IS_FAVORITED.value,
            self.request.user.is_authenticated
        )

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """
        Filter the queryset to include only recipes that are \
        in the user's shopping cart.

        Args:
            queryset (QuerySet): The initial queryset of recipes.
            name (str): The name of the filter.
            value (str): The filter value, expected to be '1' or '0',
                         but boolean, str ('True'/'False') and integers
                         1 and 0 are also accepted.

        Returns:
            QuerySet: The filtered queryset containing only recipes
            from user's shopping cart.
        """
        return filter_by_boolean(
            queryset,
            self.request.user,
            value,
            RecipeRelatedFields.IS_IN_SHOPPING_CART.value,
            self.request.user.is_authenticated
        )


class IngredientsSearchFilter(filters.SearchFilter):
    """
    Custom search filter for searching ingredients based on user input \
    upon creating new recipe.

    This filter performs a case-insensitive search for ingredients that
    match the provided search terms. It supports single-word and
    multi-word searches.

    1. **Single Word Search**:
       - Input: `?search=apple`
       - Query: This will return all ingredients containing the word
         'анис'.
         For instance, 'apple', 'apples', 'apple vinegar' etc.

    2. **Multi-Word Search**:
       - Input: `?search=app j`
       - Query: This will return ingredients containing both 'app' and
         'j'.
         For instance, 'apple jam', 'apple juice' etc.

    3. **Case-Insensitive Search**:
       - Input: `?search=aPp J`
       - Query: This will return all ingredients that contain 'aPp' and
         'J' regardless of case.
         For instance, 'apple jam', 'apple juice' etc.
    """

    def filter_queryset(self, request, queryset, view):
        """
        Filter the queryset based on the search terms provided in the request.

        Args:
            request (Request): The HTTP request containing search parameters.
            queryset (QuerySet): The initial queryset of ingredients.
            view (View): The view that is handling the request.

        Returns:
            QuerySet: The filtered queryset containing ingredients that
            match the search terms.
        """
        search_fields = self.get_search_fields(view, request)
        search_terms = self.get_search_terms(request)

        if not search_fields or not search_terms:
            return queryset

        orm_lookups = [
            f'{search_field}__icontains'
            for search_field in search_fields
        ]

        conditions = []
        for search_term in search_terms:
            queries = [
                models.Q(**{orm_lookup: search_term.lower()})
                for orm_lookup in orm_lookups
            ]
            conditions.append(reduce(operator.or_, queries))

        queryset = queryset.filter(reduce(operator.and_, conditions))

        if self.must_call_distinct(queryset, search_fields):
            queryset = queryset.distinct()

        return queryset
