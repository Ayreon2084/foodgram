from django.contrib.auth import get_user_model
from djoser import views as djoser_views
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response

from .serializers import AvatarSerializer, UserSerializer

User = get_user_model()


class UserViewSet(djoser_views.UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = LimitOffsetPagination

    def get_permissions(self):
        if self.action == 'list':
            return (AllowAny(),)
        elif self.action == 'me':
            return (IsAuthenticated(),)
        return super().get_permissions()

    @action(
        detail=False,
        url_path='me/avatar',
        permission_classes=[IsAuthenticated],
        methods=['put']
    )
    def avatar(self, request):
        user = request.user

        serializer = AvatarSerializer(
            user,
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @avatar.mapping.delete
    def delete_avatar(self, request):
        user = request.user
        user.avatar = None
        user.save()
        return Response(
            {'detail': 'Avatar has been deleted.'},
            status=status.HTTP_204_NO_CONTENT
        )


    # @action follow