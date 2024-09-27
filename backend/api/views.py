from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.http import HttpResponseRedirect
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from djoser import views as djoser_views
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (
    AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response

from users.models import FollowUser
from recipes.models import Ingredient, Recipe, Tag

from .filters import RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    AvatarSerializer, IngredientSerializer, RecipeCreateSerializer,
    RecipeDetailSerializer, TagSerializer, UserSerializer
)
from .utils import generate_short_link

User = get_user_model()


class UserViewSet(djoser_views.UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    http_method_names = ('get', 'post', 'put', 'delete',)

    def get_permissions(self):
        if self.action == 'me':
            return (IsAuthenticated(),)
        return super().get_permissions()

    @action(
        detail=False,
        url_path='me/avatar',
        permission_classes=[IsAuthenticated],
        methods=['put'],
    )
    def avatar(self, request):
        user = request.user

        serializer = AvatarSerializer(
            user,
            data=request.data,
            context={'request': request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status.HTTP_200_OK)

    @avatar.mapping.delete
    def delete_avatar(self, request):
        user = request.user
        user.avatar = None
        user.save()
        return Response(
            {'detail': 'Avatar has been deleted.'},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=False,
        url_path='subscriptions',
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        followed_users = User.objects.filter(followed__user=request.user)
        page = self.paginate_queryset(followed_users)
        if page is not None:
            serializer = UserSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = UserSerializer(followed_users, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['post'],
        url_path='subscribe',
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, pk=id)

        if user == author:
            return Response(
                {'detail': 'You can not follow yourself.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if FollowUser.objects.filter(user=user, author=author).exists():
            return Response(
                {'detail': 'You are already following this user.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        FollowUser.objects.create(user=user, author=author)
        return Response(
            {'detail': f'You are now following {author.username}.'},
            status=status.HTTP_201_CREATED
        )

    @action(
        detail=True,
        methods=['delete'],
        permission_classes=[IsAuthenticated]
    )
    def unsubscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, pk=id)

        follow = FollowUser.objects.filter(user=user, author=author).first()
        if not follow:
            return Response(
                {'detail': 'You are not following this user.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        follow.delete()
        return Response(
            {'detail': f'You have unfollowed {author.username}.'},
            status=status.HTTP_204_NO_CONTENT
        )


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)  # DjangoFilterBackend, 
    filterset_fields = ('name',)
    search_fields = ('^name',)  # ('^name', 'name__icontains',)
    max_results = 20


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.select_related(
        'author'
    ).prefetch_related('ingredients', 'tags')
    http_method_names = ('get', 'post', 'patch', 'delete',)
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update']:
            return RecipeCreateSerializer
        return RecipeDetailSerializer

    def perform_create(self, serializer):
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
            return Response({'short-link': short_link}, status=status.HTTP_200_OK)

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


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
