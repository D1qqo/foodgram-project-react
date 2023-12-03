from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """Разрешение предоставления изменений только админу."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Разрешение предоставления изменений только автору."""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user
