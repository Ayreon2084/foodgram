from django.conf import settings
from django.urls import include, path
from rest_framework.routers import DefaultRouter, SimpleRouter

from .views import IngredientViewSet, RecipeViewSet, TagViewSet, UserViewSet

app_name = 'api_v1'

Router = DefaultRouter if settings.DEBUG else SimpleRouter

api_v1 = Router()
api_v1.register(r'users', UserViewSet, basename='users')
api_v1.register(r'tags', TagViewSet, basename='tags')
api_v1.register(r'ingredients', IngredientViewSet, basename='ingredients')
api_v1.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(api_v1.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path(
        's/<str:link_suffix>/',
        RecipeViewSet.as_view({'get': 'redirect_short_link'}),
        name='short-link-redirect'
    ),
]
