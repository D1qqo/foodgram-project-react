from django.urls import include, path
from rest_framework import routers

from recipes.views import (
    IngredientViewSet,
    RecipesViewSet,
    TagViewSet,
)
from users.views import UserViewSet

app_name = 'api'
router = routers.DefaultRouter()

router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipesViewSet)
router.register('tags', TagViewSet)
router.register('users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken'))
]
