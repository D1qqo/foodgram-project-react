from django.contrib import admin

from .models import Subscribe, User


class SubscribeAdmin(admin.ModelAdmin):
    """Админка подписок."""
    list_display = ('user', 'author')


class UserAdmin(admin.ModelAdmin):
    """Админка пользователей."""
    list_display = ('email', 'username', 'first_name')
    list_filter = ('email', 'username', 'first_name')


admin.site.register(Subscribe, SubscribeAdmin)
admin.site.register(User, UserAdmin)
