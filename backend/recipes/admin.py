from django.contrib import admin

from .models import (
    Tag, Ingredient,
    IngredientRecipe,
    Recipe,
    FavoriteRecipe,
    ShoppingCart
)


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe
    extra = 1
    verbose_name = 'Ingredient in Recipe'
    verbose_name_plural = 'Ingredients in Recipe'
    fields = ('ingredient', 'amount',)
    raw_id_fields = ('ingredient',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'pub_date', 'cooking_time', 'short_link',)
    search_fields = ('name', 'author__username',)
    list_filter = ('author', 'tags',)
    inlines = (IngredientRecipeInline,)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related(
            'author'
        ).prefetch_related(
            'ingredients', 'tags'
        )


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
