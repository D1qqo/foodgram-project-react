from rest_framework.permissions import (BasePermission,
                                        IsAuthenticatedOrReadOnly,
                                        SAFE_METHODS)


class IsAdminOrReadOnly(BasePermission):
    """Разрешение предоставления изменений только админу."""
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class IsAuthorOrReadOnly(IsAuthenticatedOrReadOnly):
    """Разрешение предоставления изменений только автору."""

    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS or obj.author == request.user)
