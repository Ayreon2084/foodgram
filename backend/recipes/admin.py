from django.contrib import admin
from django.db import models

from .models import (FavoriteRecipe, Ingredient, IngredientRecipe, Recipe,
                     ShoppingCart, Tag)


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe
    extra = 1
    verbose_name = 'Ingredient in Recipe'
    verbose_name_plural = 'Ingredients in Recipe'
    fields = ('ingredient', 'amount',)
    raw_id_fields = ('ingredient',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'author', 'pub_date',
        'cooking_time', 'short_link', 'favorite_count',
    )
    search_fields = ('name', 'author__username',)
    list_filter = ('author', 'tags',)
    inlines = (IngredientRecipeInline,)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related(
            'author'
        ).prefetch_related(
            'ingredients', 'tags'
        ).annotate(
            favorite_count=models.Count('favorited_by')
        )

    def favorite_count(self, obj):
        return obj.favorite_count

    favorite_count.short_description = 'количество подписок'


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)
    search_fields = ('user__username', 'recipe__name',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)
    search_fields = ('user__username', 'recipe__name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',)
    search_fields = ('name', 'slug',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)
