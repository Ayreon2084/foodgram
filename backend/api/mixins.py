from djoser import views as djoser_views
from rest_framework import serializers, viewsets

from recipes.models import FavoriteRecipe, ShoppingCart
from users.models import FollowUser


class BaseRecipeViewSetMixin(viewsets.ModelViewSet):

    def check_favorite_recipe(self, user, recipe):
        """Check if a recipe is already in the user's favorites."""
        return FavoriteRecipe.objects.filter(user=user, recipe=recipe).exists()

    def check_shopping_cart(self, user, recipe):
        """Check if a recipe is already in the user's shopping cart."""
        return ShoppingCart.objects.filter(user=user, recipe=recipe).exists()


class BaseUserViewSetMixin(djoser_views.UserViewSet):

    def check_subscription(self, user, author):
        """Check if a user is subscribed to the author."""
        return FollowUser.objects.filter(
            user=user, author=author
        ).exists()


class TagIngredientViewSetMixin(viewsets.ReadOnlyModelViewSet):

    pagination_class = None


class SubscriptionMixin:

    def is_subscribed(self, user, author):
        request = self.context.get('request')
        if request is None or user.is_anonymous:
            return False
        if user == author:
            return False
        return user.follower.filter(author=author).exists()

    def is_valid_subscription(self, user, author):
        if user == author:
            raise serializers.ValidationError(
                'You cannot subscribe to yourself.'
            )
        if user.follower.filter(author=author).exists():
            raise serializers.ValidationError(
                'You have already followed this user.'
            )
        return True
