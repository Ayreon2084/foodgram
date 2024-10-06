from tempfile import NamedTemporaryFile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from recipes.models import (FavoriteRecipe, Ingredient, Recipe, ShoppingCart,
                            Tag)
from users.models import FollowUser

from .filters import IngredientsSearchFilter, RecipeFilter
from .mixins import (BaseRecipeViewSetMixin, BaseUserViewSetMixin,
                     TagIngredientViewSetMixin)
from .pagination import PageLimitPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (AvatarSerializer, FollowUserSerializer,
                          IngredientSerializer, RecipeCreateSerializer,
                          RecipeDetailSerializer, ShortenedRecipeSerializer,
                          TagSerializer, UserSerializer)
from .utils import (delete_temp_file, generate_shopping_cart_content,
                    get_or_create_short_link)

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

        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['post'],
        url_path='subscribe',
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id):
        user = self.request.user
        author = get_object_or_404(User, pk=id)
        recipes_limit = request.query_params.get('recipes_limit')
        serializer = FollowUserSerializer(
            author,
            context={'request': request, 'recipes_limit': recipes_limit}
        )
        if serializer.is_valid_subscription(user, author):
            FollowUser.objects.create(user=user, author=author)
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
    pagination_class = PageLimitPagination

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
    def get_link(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        full_short_link = get_or_create_short_link(request, recipe)

        return Response(
            {'short-link': full_short_link},
            status=status.HTTP_200_OK
        )

    @action(
        detail=False,
        methods=['get'],
        url_path='s/(?P<link_suffix>)',
        permission_classes=[AllowAny]
    )
    def redirect_short_link(self, request, link_suffix):
        recipe = get_object_or_404(Recipe, short_link=link_suffix)
        url = f'{settings.ABSOLUTE_DOMAIN}/recipes/{recipe.id}/'
        return redirect(url)

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

        content = generate_shopping_cart_content(user, shopping_cart_items)

        with NamedTemporaryFile(delete=False, suffix=".txt") as tmp_file:
            tmp_file.write(content.encode('utf-8'))
            tmp_file_path = tmp_file.name

        response = FileResponse(
            open(tmp_file_path, 'rb'),
            content_type='text/plain'
        )
        response['Content-Disposition'] = (
            f'attachment; filename="shopping_list_{user.username}.txt"'
        )

        response.close = lambda: delete_temp_file(tmp_file_path)
        return response


class TagViewSet(TagIngredientViewSetMixin):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
