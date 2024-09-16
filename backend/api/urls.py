from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserViewSet

api_v1 = DefaultRouter()
api_v1.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(api_v1.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
