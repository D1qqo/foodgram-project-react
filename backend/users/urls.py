from django.urls import include, path
from rest_framework import routers

from .views import 

router = routers.DefaultRouter()

router.register(r'recipes', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
]