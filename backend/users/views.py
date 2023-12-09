from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from api.pagination import PagePagination
from api.serializers import UsersInformationSerializer, SubscribeSerializer
from .models import Subscribe, User


class UsersViewSet(UserViewSet):
    """Вьюсет юзера и подписок."""
    queryset = User.objects.all()
    serializer_class = UsersInformationSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = PagePagination

    @action(methods=['POST', 'DELETE'], detail=True,
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        subscription = Subscribe.objects.filter(
            user=user, author=author)
        if request.method == 'POST':
            if subscription.exists():
                return Response({'error': 'Вы не можете подписаться снова'},
                                status=status.HTTP_400_BAD_REQUEST)
            if user == author:
                return Response({'error': 'Вы не можете подписаться на себя'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = SubscribeSerializer(author,
                                             context={'request': request})
            Subscribe.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if subscription.exists():
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'error': 'Вы не подписаны на этого автора'},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        subscribes = User.objects.filter(subscribing__user=user)
        page = self.paginate_queryset(subscribes)
        serializer = SubscribeSerializer(
            page, many=True,
            context={'request': request})
        return self.get_paginated_response(serializer.data)
