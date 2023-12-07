from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)

from api.pagination import PagePagination
from api.serializers import UsersInformationSerializer, SubscribeSerializer
from .models import Subscribe, User


class UsersViewSet(UserViewSet):
    """Вьюсет юзера."""
    queryset = User.objects.all()
    serializer_class = UsersInformationSerializer
    permission_classes = IsAuthenticatedOrReadOnly
    pagination_class = PagePagination
