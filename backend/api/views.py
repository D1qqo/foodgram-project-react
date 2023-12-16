from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as BaseUserViewSet
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import RecipePagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    FavoriteSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeSerializer,
    ShoppingListSerializer,
    SubscribeSerializer,
    TagSerializer,
    UserSerializer,
)
from recipes.models import (
    Ingredient,
    IngredientsInRecipe,
    Recipes,
    Tag
)
from users.models import Subscribe, User


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnly, )
    pagination_class = RecipePagination
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter

    def create(self, request):
        if request.user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = RecipeCreateSerializer(
            data=request.data, context={'request': request}
        )
        if serializer.is_valid(raise_exception=True):
            recipe = serializer.save()
            return Response(
                RecipeSerializer(
                    recipe, context={'request': request}
                ).data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return RecipeCreateSerializer

    def create_fav_shop(self, request, pk, current_ser):
        user = request.user
        if not Recipes.objects.filter(pk=pk).exists():
            return Response({'error': 'Этого рецепта нет в списке'},
                            status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'POST':
            serializer = current_ser(
                data={'user': user.id, 'recipe': pk},
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_fav_shop(self, request, pk, current_ser):
        user = request.user
        recipe = get_object_or_404(Recipes, pk=pk)
        object = current_ser.Meta.model.objects.filter(
            user=user, recipe=recipe
        )
        if request.method == 'DELETE':
            if object.exists():
                object.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'error': 'Этого рецепта нет в списке'},
                                status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.create_fav_shop(request, pk, FavoriteSerializer)
        elif request.method == 'DELETE':
            return self.delete_fav_shop(request, pk, FavoriteSerializer)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(permissions.IsAuthenticatedOrReadOnly,)
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.create_fav_shop(request, pk, ShoppingListSerializer)
        elif request.method == 'DELETE':
            return self.delete_fav_shop(request, pk, ShoppingListSerializer)

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        if request.user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        ingredients = (IngredientsInRecipe.objects.filter(
            recipe__shopping_cart__user=request.user
        ).order_by('ingredients__name').values(
            'ingredients__name', 'ingredients__measurement_unit'
        ).annotate(amount=Sum('amount')))
        ingr_list = []
        ingr_list += 'Список покупок:\n  '
        for ingredient in ingredients:
            ingr_list.append(
                f'\n'
                f'{ingredient.get("ingredients__name").title()}:  '
                f'{ingredient.get("amount") }'
                f'({ingredient.get("ingredients__measurement_unit")}) '
            )
        response = FileResponse(
            ingr_list,
            content_type='text/plain'
        )
        response['Content-Disposition'] = (
            'attachment; filename=Shopping_List.txt'
        )
        return response


class UserViewSet(BaseUserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = RecipePagination
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = (IsAuthenticated,)
        return super().get_permissions()

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        subscription = Subscribe.objects.filter(
            user=user,
            author=author
        )
        if request.method == 'POST':
            if subscription.exists():
                return Response({'error': 'Вы уже подписаны'},
                                status=status.HTTP_400_BAD_REQUEST)
            if user == author:
                return Response({'error': 'Невозможно подписаться на себя'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = SubscribeSerializer(
                author, context={'request': request}
            )
            Subscribe.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if subscription.exists():
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'error': 'Вы не подписаны на этого пользователя'},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=['GET'],
        url_path='subscriptions',
        url_name='subscriptions',
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(author__user=request.user)
        serializer = SubscribeSerializer(
            self.paginate_queryset(queryset),
            context={'request': request},
            many=True
        )
        return self.get_paginated_response(serializer.data)
