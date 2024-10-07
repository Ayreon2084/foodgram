from django.contrib.auth import get_user_model
from drf_base64.fields import Base64ImageField
from rest_framework import serializers

from common.constants import MAX_VALUE, MIN_VALUE
from recipes.models import Ingredient, IngredientRecipe, Recipe, Tag

from .mixins import SubscriptionMixin

User = get_user_model()


class UserSerializer(SubscriptionMixin, serializers.ModelSerializer):

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed'
        )

    def get_is_subscribed(self, author):
        user = self.context['request'].user
        return self.is_subscribed(user, author)


class AvatarSerializer(serializers.ModelSerializer):

    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')

        if instance.avatar and request:
            avatar_url = request.build_absolute_uri(instance.avatar.url)
            representation['avatar'] = avatar_url
            return representation
        return representation


class FollowUserSerializer(SubscriptionMixin, serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name',
            'last_name', 'is_subscribed', 'recipes',
            'recipes_count', 'avatar'
        )

    def get_is_subscribed(self, author):
        user = self.context['request'].user
        return self.is_subscribed(user, author)

    def get_recipes(self, obj):
        recipes_limit = self.context.get('recipes_limit')
        recipes = obj.recipes.all()

        if recipes_limit:
            try:
                recipes_limit = int(recipes_limit)
                recipes = recipes[:recipes_limit]
            except ValueError:
                pass

        return ShortenedRecipeSerializer(
            recipes,
            many=True,
            context=self.context
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def validate(self, data):
        user = self.context['request'].user
        author = data.get('author')
        self.is_valid_subscription(user, author)
        return data


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField(
        min_value=MIN_VALUE,
        max_value=MAX_VALUE
    )

    class Meta:
        model = IngredientRecipe
        fields = ['id', 'amount']


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug',)


class RecipeCreateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    ingredients = IngredientInRecipeSerializer(many=True)
    cooking_time = serializers.IntegerField(
        min_value=MIN_VALUE,
        max_value=MAX_VALUE
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'ingredients',
            'image',
            'name',
            'text',
            'cooking_time'
        )

    def validate(self, data):
        required_fields = (
            'tags',
            'ingredients',
            'name',
            'text',
            'cooking_time',
        )
        missing_field = {}

        for field in required_fields:
            if not data.get(field):
                missing_field[field] = f'{field} field is required.'

        if missing_field:
            raise serializers.ValidationError(missing_field)
        return data

    def validate_tags(self, tags):
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                'You must not repeat the same tags.'
            )

        return tags

    def validate_ingredients(self, ingredients):
        check_duplicates = set([
            (ingredient['id'], ingredient['amount'])
            for ingredient in ingredients
        ])
        if len(check_duplicates) != len(ingredients):
            raise serializers.ValidationError(
                'You must not repeat the same ingredients.'
            )

        for ingredient in ingredients:
            if not Ingredient.objects.filter(id=ingredient['id']).exists():
                raise serializers.ValidationError(
                    f'Ingredient with {ingredient["id"]} id '
                    'does not exist.'
                )

        return ingredients

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)

        recipe.tags.set(tags)

        for ingredient in ingredients:
            IngredientRecipe.objects.create(
                recipe=recipe,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount']
            )

        return recipe

    def update(self, recipe, validated_data):
        tags = validated_data.get('tags')
        ingredients = validated_data.get('ingredients')
        recipe.image = validated_data.get('image', recipe.image)
        recipe.name = validated_data.get('name', recipe.name)
        recipe.text = validated_data.get('text', recipe.text)
        recipe.cooking_time = validated_data.get(
            'cooking_time', recipe.cooking_time
        )

        if tags:
            recipe.tags.clear()
            recipe.tags.set(tags)

        if ingredients:
            recipe.ingredients.clear()
            for ingredient in ingredients:
                IngredientRecipe.objects.create(
                    recipe=recipe,
                    ingredient_id=ingredient['id'],
                    amount=ingredient['amount']
                )

        recipe.save()
        return recipe

    def to_representation(self, recipe):
        return RecipeDetailSerializer(recipe, context=self.context).data


class RecipeDetailSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_ingredients(self, obj):
        """Return ingredients with amount in the response."""
        ingredients = obj.ingredient_recipe.select_related('ingredient')
        return [
            {
                'id': ingredient.ingredient.id,
                'name': ingredient.ingredient.name,
                'measurement_unit': ingredient.ingredient.measurement_unit,
                'amount': ingredient.amount
            }
            for ingredient in ingredients
        ]

    def get_tags(self, obj):
        """Return serialized tags."""
        tags = obj.tags.all()
        return TagSerializer(tags, many=True).data

    def get_is_favorited(self, recipe):
        request = self.context.get('request')
        if request and not request.user.is_anonymous:
            return request.user.favorites.filter(recipe=recipe).exists()
        return False

    def get_is_in_shopping_cart(self, recipe):
        request = self.context.get('request')
        if request and not request.user.is_anonymous:
            return request.user.shopping_cart.filter(recipe=recipe).exists()
        return False


class ShortenedRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
