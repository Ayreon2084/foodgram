import os
from tempfile import NamedTemporaryFile

from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.encoding import smart_str
from django.utils.timezone import now
from django_filters.rest_framework import DjangoFilterBackend
from djoser import views as djoser_views
from recipes.models import (FavoriteRecipe, Ingredient, Recipe, ShoppingCart,
                            Tag)
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from users.models import FollowUser

from .filters import IngredientsSearchFilter, RecipeFilter
from .mixins import (
    BaseRecipeViewSetMixin, BaseUserViewSetMixin,
    TagIngredientViewSetMixin
)
from .pagination import PageLimitPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (AvatarSerializer, FollowUserSerializer,
                          IngredientSerializer, RecipeCreateSerializer,
                          RecipeDetailSerializer, ShortenedRecipeSerializer,
                          TagSerializer, UserSerializer)
from .utils import generate_short_link  # generate_shopping_cart_content

User = get_user_model()


class UserViewSet(BaseUserViewSetMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    http_method_names = ('get', 'post', 'put', 'delete',)
    pagination_class = PageLimitPagination

    def get_permissions(self):
        if self.action == 'me':
            return (IsAuthenticated(),)
        return super().get_permissions()

    @action(
        detail=False,
        url_path='me/avatar',
        methods=['put'],
        permission_classes=[IsAuthenticated]
    )
    def avatar(self, request):
        serializer = AvatarSerializer(
            request.user,
            data=request.data,
            context={'request': request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status.HTTP_200_OK)

    @avatar.mapping.delete
    def delete_avatar(self, request):
        request.user.avatar = None
        request.user.save()
        return Response(
            {'detail': 'Avatar has been deleted.'},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=False,
        methods=['get'],
        url_path='subscriptions',
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        followed_users = User.objects.filter(followed__user=request.user)
        page = self.paginate_queryset(followed_users)
        recipes_limit = request.query_params.get('recipes_limit')

        serializer = FollowUserSerializer(
            page or followed_users,
            many=True,
            context={'request': request, 'recipes_limit': recipes_limit}
        )
        return (
            self.get_paginated_response(serializer.data)
            if page else Response(serializer.data, status=status.HTTP_200_OK)
        )

    @action(
        detail=True,
        methods=['post'],
        url_path='subscribe',
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id):
        user = self.request.user
        author = get_object_or_404(User, pk=id)

        # if user == author:
        #     return Response(
        #         {'detail': 'You can not be subscribed on yourself.'},
        #         status=status.HTTP_400_BAD_REQUEST
        #     )

        # if self.check_subscription(user, author):
        #     return Response(
        #         {'detail': 'You have already followed this user.'},
        #         status=status.HTTP_400_BAD_REQUEST
        #     )
        serializer = FollowUserSerializer(
            context={'request': request}
        )
        if serializer.is_valid_subscription(user, author):
            FollowUser.objects.create(user=user, author=author)

        recipes_limit = request.query_params.get('recipes_limit')

        serializer = FollowUserSerializer(
            author,
            context={'request': request, 'recipes_limit': recipes_limit}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, id):
        user = self.request.user
        author = get_object_or_404(User, pk=id)

        if not self.check_subscription(user, author):
            return Response(
                {'detail': 'You have not followed this user.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        subscribtion = get_object_or_404(FollowUser, user=user, author=author)
        subscribtion.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(TagIngredientViewSetMixin):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientsSearchFilter, filters.SearchFilter,)
    search_fields = ('name',)
    max_results = 20


class RecipeViewSet(BaseRecipeViewSetMixin):
    queryset = Recipe.objects.prefetch_related(
        'ingredients',
        'tags',
    ).select_related(
        'author'
    )
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    http_method_names = ('get', 'post', 'patch', 'delete',)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update']:
            return RecipeCreateSerializer
        return RecipeDetailSerializer

    def perform_create(self, serializer):
        serializer.is_valid(raise_exception=True)
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['get'],
        url_path='get-link',
        permission_classes=[AllowAny]
    )
    def get_link(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)

        if recipe.short_link:
            short_link = request.build_absolute_uri(f'/s/{recipe.short_link}/')
            return Response(
                {'short-link': short_link}, status=status.HTTP_200_OK
            )

        short_link_suffix = generate_short_link()

        recipe.short_link = short_link_suffix
        recipe.save()

        short_link = request.build_absolute_uri(f'/s/{short_link_suffix}/')
        return Response({'short-link': short_link}, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['get'],
        url_path='s/(?P<link_suffix>[^/]+)',
        permission_classes=[AllowAny]
    )
    def redirect_short_link(self, request, link_suffix):
        recipe = get_object_or_404(Recipe, short_link=link_suffix)
        return HttpResponseRedirect(f'/recipes/{recipe.id}')

    @action(
        detail=True,
        methods=['post'],
        url_path='favorite',
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if self.check_favorite_recipe(user, recipe):
            return Response(
                {'detail': 'You have already followed this recipe.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        FavoriteRecipe.objects.create(
            user=user,
            recipe=recipe
        )
        serializer = ShortenedRecipeSerializer(
            recipe,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def unfavorite(self, request, pk):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if not self.check_favorite_recipe(user, recipe):
            return Response(
                {'detail': 'You have not followed this recipe.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        favorite = get_object_or_404(FavoriteRecipe, user=user, recipe=recipe)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post'],
        url_path='shopping_cart',
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if self.check_shopping_cart(user, recipe):
            return Response(
                {'detail': 'This recipe is already in shopping cart.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        ShoppingCart.objects.create(user=user, recipe=recipe)

        serializer = ShortenedRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def remove_from_shopping_cart(self, request, pk):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if not self.check_shopping_cart(user, recipe):
            return Response(
                {'detail': 'This recipe is not in shopping cart.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        shopping_cart_item = get_object_or_404(
            ShoppingCart, user=user, recipe=recipe
        )
        shopping_cart_item.delete()
        return Response(
            {'detail': 'Recipe removed from shopping cart.'},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=False,
        methods=['get'],
        url_path='download_shopping_cart',
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        user = request.user
        shopping_cart_items = ShoppingCart.objects.filter(
            user=user
        ).prefetch_related('recipe__ingredients')

        ingredient_totals = {}

        for item in shopping_cart_items:
            recipe = item.recipe
            for ingredient_recipe in recipe.ingredient_recipe.all():
                ingredient = ingredient_recipe.ingredient
                key = (ingredient.name, ingredient.measurement_unit)
                if key in ingredient_totals:
                    ingredient_totals[key] += ingredient_recipe.amount
                else:
                    ingredient_totals[key] = ingredient_recipe.amount

        content_lines = ["# Shopping List\n"]
        content_lines.append(
            f"Generated on: {now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )
        content_lines.append("![Site Logo](link_to_logo.png)\n")

        for recipe in shopping_cart_items.values_list(
            'recipe__name', flat=True
        ).distinct():
            content_lines.append(f"\n## {recipe}\n")

        content_lines.append("\n### Ingredients\n")
        for (name, unit), amount in ingredient_totals.items():
            content_lines.append(f"- [ ] {name} - {amount} {unit}\n")

        with NamedTemporaryFile(delete=False, suffix=".md") as tmp_file:
            tmp_file.write("\n".join(content_lines).encode('utf-8'))
            tmp_file_path = tmp_file.name

        with open(tmp_file_path, 'rb') as md_file:
            response = HttpResponse(
                md_file.read(), content_type='text/markdown'
            )
            response['Content-Disposition'] = (
                f'attachment; filename="shopping_cart_{user.username}.md"'
            )

        os.remove(tmp_file_path)

        return response


class TagViewSet(TagIngredientViewSetMixin):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
